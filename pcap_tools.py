#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
音视频合成
author:xzh
"""

import os
import subprocess
import socket
import datetime
import dpkt
import re
import time
import collections
import math

from Dict_data_manager import Deal_dict
from log import log
from operation import Operation
from get_config import get_config_from_json

PROTO_BOOL = {'udp': '17', 'tcp': '6', 'ntp': '123'}
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
PCAP_PATH = os.path.join(CUR_PATH, "upload")
DUMP_PATH = os.path.join(CUR_PATH, "mp4_tools")
VIDEO_PATH = os.path.join(CUR_PATH, "video_data")
START_TIME = 0  # Time变化时记作一个开始时间
START_SEQ = 0  # 记录开始的seq
DATA_LEN = 0  # 数据长度
I_s = 0
WAVNAMELIST = []
MP4NAMELIST = []
protocol_dic = {17: 'UDP', 1: 'ICMP', 2: 'IGMP', 6: 'TCP',
                '800': 'IP', '86DD': 'IPv6', '806': 'ARP', '8035': 'RARP',
                '8863': 'PPPoE discovery', '8864': 'PPPoE session'}
media_server_ip = ['103.20.113.11', '103.20.113.12', '103.20.113.13', '103.20.113.14']
nal_unit_hdr_dic = {1: 'P', 7: 'SPS', 8: 'PPS', 28: 'FU-A', 5: 'IDR'}


class H264SPSPaser(object):
    startBit = 0

    def getStartBit(self):
        return self.startBit

    def u(self, data, bitCnt, StartBit):
        """
        从数据流data中第StartBit位开始读，读bitCnt位，以无符号整形返回
        :param data:
        :param bitCnt:
        :param StartBit:
        :return:
        """
        ret = 0
        start = StartBit
        for i in range(bitCnt):
            ret <<= 1
            if (data[int(start / 8)]) & ((0x80 >> (start % 8))) != 0:
                ret += 1
            start += 1
        self.startBit = StartBit + bitCnt
        return ret

    def ue(self, data, StartBit):
        """
        无符号指数哥伦布编码
        :param data:
        :param StartBit:
        :return:
        """
        leadingZeroBits = -1
        tempStartBit = StartBit
        b = 0
        while b != 1:
            b = self.u(data, 1, tempStartBit)
            tempStartBit += 1
            leadingZeroBits += 1
        ret = int(math.pow(2, leadingZeroBits) - 1 + self.u(data, leadingZeroBits, tempStartBit))
        self.startBit = tempStartBit + leadingZeroBits
        return ret

    def se(self, data, StartBit):
        """
        有符号指数哥伦布编码
        :param data:
        :param StartBit:
        :return:
        """
        codeNum = int(self.ue(data, StartBit))
        ret = int(math.pow(-1, codeNum + 1) * math.ceil(codeNum / 2))
        return ret


class PcapTools(object):
    def __init__(self, pacp, cur_path):
        self.op = Operation()
        self.pacp_name = pacp.split("/")[-1]
        self.pcap_path = pacp
        self.upload = os.path.join(cur_path, "upload")
        self.dump_path = os.path.join(cur_path, "mp4_tools")
        self.video_path = os.path.join(cur_path, "video_data")
        audio_coding, video_coding, begin, max_port, next_port, \
        next_bfcp_port, video_model, fps, re_trs = get_config_from_json()
        global audio_coding, video_coding, begin, max_port, next_port, next_bfcp_port, video_model, fps, re_trs

    def writer_new_pcap(self, path, main_ip=None, server_ip=None, port_list=None, ip_port=None,
                        filter_type=None, filter_ip=False, filter_time=None):
        seq_list = []
        new_pcap = open(path, "wb")
        writer = dpkt.pcap.Writer(new_pcap)
        f = open(self.pcap_path, 'rb')
        if 'pcapng' in self.pcap_path:
            packets = dpkt.pcapng.Reader(f)
        else:
            packets = dpkt.pcap.Reader(f)
        eth_b = 0
        if ip_port != None:
            if "." in ip_port:
                main_ip = ip_port
            else:
                port_list = ip_port
        for ts, buf in packets:
            if eth_b == 0:
                try:
                    data = dpkt.ethernet.Ethernet(buf)
                    eth = True
                except:
                    data = dpkt.sll.SLL(buf)
                    eth = False
                eth_b = 1
            try:
                eth_info = self.__filter_condition(ts, buf, main_ip=main_ip, server_ip=server_ip,
                                                   port_list=port_list, filter_type=filter_type, filter_ip=filter_ip,
                                                   eth_type=eth)
                if eth_info == False:
                    continue
                #log.info('eth_info:'.format(eth_info))
                if filter_time != None:  # 过滤时间
                    if eth_info['time'] < filter_time:
                        continue
                seq = dpkt.rtp.RTP(eth_info['ip'].data.data).seq
                if re_trs == 'True':
                    if seq == 65535:
                        seq_list.clear()
                    if seq not in seq_list:
                        seq_list.append(seq)
                        writer.writepkt(eth_info['eth'], ts=ts)  # 如果不加ts参数的话，这个数据包的时间戳默认是当前时间！
                        new_pcap.flush()
                else:
                    writer.writepkt(eth_info['eth'], ts=ts)  # 如果不加ts参数的话，这个数据包的时间戳默认是当前时间！
                    new_pcap.flush()
            except:
                continue
        new_pcap.close()

    def __filter_condition(self, time, buf, main_ip=None, server_ip=None, port_list=None,
                           filter_type=None, filter_ip=False, eth_type=True, proto='udp'):

        if eth_type:
            eth = dpkt.ethernet.Ethernet(buf)
        else:
            eth = dpkt.sll.SLL(buf)
        now_date = datetime.datetime.utcfromtimestamp(time) + datetime.timedelta(hours=8)
        ip = eth.data
        src_ip = self.op.inet_to_str(ip.src)
        dst_ip = self.op.inet_to_str(ip.dst)
        """对地址的过滤"""
        if main_ip != None:
            if filter_ip == False:  # 对地址过滤
                if src_ip == main_ip or dst_ip == main_ip:
                    pass
                else:
                    return False
            else:
                if src_ip != main_ip:
                    return False
        if server_ip != None:
            if filter_ip == False:
                if src_ip == server_ip or dst_ip == server_ip:
                    pass
                else:
                    return False
            else:
                if dst_ip != server_ip:
                    return False
        if port_list != None:
            if ip.data.sport not in port_list and ip.data.dport not in port_list:
                return False
        if proto in ['udp', 'UDP']:
            proto_type = dpkt.udp.UDP
        else:
            proto_type = dpkt.tcp.TCP
        if filter_type != None:  # 对报文类型过滤
            if filter_type in ["tcp", "TCP"]:
                p_type = dpkt.tcp.TCP
                data = ip.data
            elif filter_type in ["udp", "UDP"]:
                p_type = dpkt.udp.UDP
                data = ip.data
            elif filter_type in ["rtp", "RTP"]:
                p_type = proto_type
                data = dpkt.rtp.RTP(ip.data.data)
            elif filter_type in ["ntp", "NTP"]:
                p_type = proto_type
                data = dpkt.ntp.NTP(ip.data.data)
            elif filter_type in ["sip", "SIP"]:
                p_type = dpkt.udp.UDP
                if ("200 OK" in repr(ip) or "INVITE" in repr(ip)) and ip.len == 1500:
                    data = ip.data.data
                else:
                    try:
                        data = dpkt.sip.Request(ip.data.data)
                    except:
                        data = dpkt.sip.Response(ip.data.data)
            else:
                p_type = ip.data
            if not isinstance(ip.data, p_type):
                return False
        eth_info = {}
        eth_info["time"] = now_date
        eth_info["eth"] = eth
        eth_info["ip"] = ip
        eth_info['buf'] = buf
        # print(eth_info)
        try:
            eth_info[filter_type] = data
            # print(eth_info)
            return eth_info
        except:
            return eth_info

    def _filter_SPS(self, pcap):
        """过滤sps报文，返回data数据"""
        try:
            len_num = pcap["ip"].len
            if len_num < 100:  # 过滤sps报文
                data = pcap["rtp"].data
                bin_num = self.op.bin2text(self.op.dec2bin(data[0]))
                sps_num = bin_num[3:8]
                if int(self.op.bin2dec(sps_num)) == 7:
                    now_date = pcap["time"]
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False

    def get_mp4_from_pcap(self, pacp, port, file_name):
        """输入错不带音频的mp4文件"""
        rtp_dump = os.path.join(self.dump_path, "rtp_dump")
        h264_path = os.path.join(self.video_path, "{}.h264".format(file_name))
        h264_command = "{} -f {}  -p {} -c {} -o {} -v".format(rtp_dump, pacp, port, video_model, h264_path)
        log.info('h264_command:{}'.format(h264_command))
        subprocess.call(h264_command, shell=True)
        time.sleep(1)
        mp4_path = os.path.join(self.video_path, "no_a_{}.mp4".format(file_name))
        ffmpeg = os.path.join(DUMP_PATH, "ffmpeg")
        mp4_command = "{} -r {} -i {} -vcodec copy {}".format(ffmpeg, fps, h264_path, mp4_path)
        log.info('mp4_command:{}'.format(mp4_command))
        subprocess.call(mp4_command, shell=True)
        time.sleep(1)
        mp4name = re.compile('/video_data/(.*.mp4)').findall(mp4_path)
        for i in mp4name:
            MP4NAMELIST.append(i)

    def get_audio_from_pcap(self, pcap, port, audio_type, file_name):
        """从报文中获取音频"""
        wav_path = os.path.join(self.video_path, "{}.wav".format(file_name))
        rtp_dump_audio = os.path.join(self.dump_path, "rtp_dump_audio")
        audio_command = "{} -f {} -c {} -o {} -p {}".format(rtp_dump_audio, pcap, audio_type, wav_path, port)
        log.info('audio_command:{}'.format(audio_command))
        subprocess.call(audio_command, shell=True)
        wavname = re.compile('/video_data/(.*.wav)').findall(wav_path)
        for i in wavname:
            WAVNAMELIST.append(i)

    def get_all_name(self):
        return MP4NAMELIST, WAVNAMELIST

    def get_merge_audio_mp4(self, file_name):
        """获取合成音频和视频的mp4文件"""
        wav_path = os.path.join(self.video_path, "{}.wav".format(file_name))
        mp4_path = os.path.join(self.video_path, "no_a_{}.mp4".format(file_name))
        out_mp4_path = os.path.join(self.video_path, "{}.mp4".format(file_name))
        ffmpeg = os.path.join(DUMP_PATH, "ffmpeg")
        merge_command = "{} -i {} -i {} -c:v copy -c:a aac -strict experimental {}". \
            format(ffmpeg, mp4_path, wav_path, out_mp4_path)
        log.info('merge_command:{}'.format(merge_command))
        subprocess.call(merge_command, shell=True)

    def get_I_frame_time(self, pcap_path, src_ip):
        """获取I帧的时间"""
        eth_b = 0
        with open(pcap_path, 'rb') as f:
            if 'pcapng' in pcap_path:
                pcap = dpkt.pcapng.Reader(f)
            else:
                pcap = dpkt.pcap.Reader(f)
            for timestamp, buf in pcap:
                if eth_b == 0:
                    try:
                        dpkt.ethernet.Ethernet(buf)
                        eth = True
                    except:
                        eth = False
                    eth_b = 1
                try:
                    eth_info = self.__filter_condition(timestamp, buf, main_ip=src_ip, eth_type=eth, filter_type="rtp",
                                                       filter_ip=True)
                    if eth_info == False:
                        continue
                    I_s = self._filter_SPS(eth_info)

                    if I_s:
                        return eth_info['time']
                except:
                    continue

    def get_rtp_pcap(self, port_info):
        """
        根据源ip和端口提取新的报文
        :param port_info: 传入提取rtp流的音视频端口和源地址
        :return:
        """
        main_ip = port_info['src']
        I_time = self.get_I_frame_time(self.pcap_path, main_ip)
        new_pcap_path = os.path.join(self.upload, "{}.pcap".format(main_ip))
        try:
            audio_port = port_info["audio_port"]
        except:
            audio_port = ''
        video_port = port_info["video_port"]
        self.writer_new_pcap(new_pcap_path, main_ip=main_ip, port_list=[audio_port, video_port],
                             filter_ip=True, filter_time=I_time)
        return new_pcap_path


    def get_video_mp4(self, src, dst, audio_type):
        pcap_name = self.pacp_name.split(".")[0]
        try:
            rtp_pcap = self.get_rtp_pcap(src)
        # 从报文中提取I帧以后的rtp流报文
        except Exception as e:
            log.error(e)
            return
        ip = src['src']
        file_name = pcap_name + '_' + ip
        try:
            audio_port = dst["audio_port"]
        except:
            audio_port = ''
        video_port = dst["video_port"]
        self.get_mp4_from_pcap(rtp_pcap, video_port, file_name)
        if audio_port != "":
            self.get_audio_from_pcap(rtp_pcap, audio_port, audio_type, file_name)
            self.get_merge_audio_mp4(file_name)
        file_name = "{}.mp4".format(file_name)
        is_file = self.op.judge_file(file_name, self.video_path)
        if not is_file:
            return ""
        return file_name

    def out_audio_and_video_to_mp4(self, port_info_):
        """输出带音频的mp4文件"""
        MP4NAMELIST.clear()
        WAVNAMELIST.clear()
        pcap_name = self.pacp_name.split(".")[0]
        old_path = os.path.join(self.video_path, "*{}*".format(pcap_name))
        subprocess.call("rm -rf {}".format(old_path), shell=True)
        port_info = port_info_
        if "audio_type" not in port_info.keys():
            audio_type = None
        else:
            audio_type = port_info['audio_type']

        def get_audio(src_or_dst):
            if port_info["src"].get('video_port') is None:
                ip = port_info[src_or_dst]['src']
                file_name = pcap_name + '_' + ip
                audio_port = port_info[src_or_dst]["audio_port"]
                if audio_port != "":
                    self.get_audio_from_pcap(self.pcap_path, audio_port, audio_type, file_name)

        get_audio('src')
        get_audio('dst')
        if port_info["src"].get('video_port') is not None:
            global fps
            fps = self.__get_fps(port_info["src"]['video_port'], port_info["dst"]['video_port'])
        out_mp41 = self.get_video_mp4(port_info["src"], port_info["dst"], audio_type)
        out_mp42 = self.get_video_mp4(port_info["dst"], port_info["src"], audio_type)
        log.info("视频文件：{}{}".format(out_mp41, out_mp42))
        return [out_mp41, out_mp42]

    def __get_fps(self, _src_port, _dst_port):
        frame_rate_list = []
        mark_n = 0
        frame_rate_time_list = []
        two_way_channel = 0
        with open(self.pcap_path, 'rb') as f:
            if '.pcapng' in self.pcap_path:
                packet = dpkt.pcapng.Reader(f)
                # 兼容pacpng格式报文
            else:
                packet = dpkt.pcap.Reader(f)
            log.info('解析中.....')
            n = 0
            for timestamp, buf in packet:
                try:
                    eth = dpkt.ethernet.Ethernet(buf)
                except:
                    eth = dpkt.sll.SLL(buf)
                ip = eth.data
                now_time = datetime.datetime.utcfromtimestamp(timestamp) + datetime.timedelta(hours=8)
                try:
                    src_port = ip.data.sport
                    dst_port = ip.data.dport
                    rtp = dpkt.rtp.RTP(ip.data.data)
                    if (src_port == _src_port and dst_port == _dst_port):
                        mark = rtp.m
                        if mark == 0:
                            continue
                        if mark == 1 and n == 0:
                            n += 1
                            old = now_time
                            frame_rate_time_list.append(old)
                        if mark == 1 and (now_time - old).seconds < 1:
                            mark_n += 1
                        elif mark == 1 and (now_time - old).seconds >= 1:
                            frame_rate_list.append(mark_n)
                            old = now_time
                            frame_rate_time_list.append(old)
                            mark_n = 1
                            two_way_channel = 1
                    if (src_port == _dst_port and dst_port == _src_port and two_way_channel == 0):
                        mark = rtp.m
                        if mark == 0:
                            continue
                        if mark == 1 and n == 0:
                            n += 1
                            old = now_time
                            frame_rate_time_list.append(old)
                        if mark == 1 and (now_time - old).seconds < 1:
                            mark_n += 1
                        elif mark == 1 and (now_time - old).seconds >= 1:
                            frame_rate_list.append(mark_n)
                            old = now_time
                            frame_rate_time_list.append(old)
                            mark_n = 1
                except:
                    pass
        frame_rate_len = []
        try:
            for rate_len in range(1, len(frame_rate_list) + 1):
                frame_rate_len.append(rate_len)
            min_frame_rate = min(frame_rate_list)
            max_frame_rate = max(frame_rate_list)
            avg_frame_rate = int(sum(frame_rate_list) / len(frame_rate_list))
            min_frame_rate_time = frame_rate_time_list[frame_rate_list.index(min_frame_rate)]
            max_frame_rate_time = frame_rate_time_list[frame_rate_list.index(max_frame_rate)]
            if 'pcapng' in self.pcap_path:
                num = 2
            else:
                num = 1
            log.info("最小帧率（对应的时间）:{}time:{}".format(min_frame_rate / num, min_frame_rate_time))
            log.info("最大帧率（对应的时间）:{}time:{}".format(max_frame_rate / num, max_frame_rate_time))
            log.info("总帧数：{}".format(sum(frame_rate_list) / num))
            log.info("平均帧率:{}".format(avg_frame_rate / num))
        except:
            num = 1
            avg_frame_rate = fps
            log.info("平均帧率(解析帧率失败，按预设帧率解析):{}".format(avg_frame_rate / num))
        return avg_frame_rate / num

    def __get_the_ip(self):
        self.tcp2udp()
        ip_dict2 = []
        with open(self.pcap_path, 'rb') as f:
            if '.pcapng' in self.pcap_path:
                packet = dpkt.pcapng.Reader(f)
                # 兼容pacpng格式报文
            else:
                packet = dpkt.pcap.Reader(f)
            log.info('解析中.....')
            for timestamp, buf in packet:
                try:
                    try:
                        eth = dpkt.ethernet.Ethernet(buf)
                    except:
                        eth = dpkt.sll.SLL(buf)
                    ip = eth.data
                    src = socket.inet_ntop(socket.AF_INET, ip.src)
                    dst = socket.inet_ntop(socket.AF_INET, ip.dst)
                    src_port = ip.data.sport
                    dst_port = ip.data.dport
                    rtp = dpkt.rtp.RTP(ip.data.data)
                    payload_type = rtp.pt
                    try:
                        _type = audio_coding[payload_type]
                    except:
                        _type = video_coding[payload_type]
                    try:
                        if dpkt.udp.UDP(ip.data.data):
                            if {'src': {'ip': src, 'port': src_port}, 'dst': {'ip': dst, 'port': dst_port},
                                'port_type': _type} not in ip_dict2:
                                if src_port % 2 == 0 and dst_port % 2 == 0:
                                    if src_port >= begin or dst_port >= begin:
                                        ip_dict2.append(
                                            {'src': {'ip': src, 'port': src_port}, 'dst': {'ip': dst, 'port': dst_port},
                                             'port_type': _type})
                    except:
                        pass
                except:
                    pass
        log.info('解析完成')
        return ip_dict2

    def get_the_ip(self):
        audio_coding, video_coding, begin, max_port, next_port, \
        next_bfcp_port, video_model, fps, re_trs = get_config_from_json()
        global audio_coding, video_coding, begin, max_port, next_port, next_bfcp_port, video_model, fps, re_trs
        ip_dict2 = self.__get_the_ip()
        _video = []
        _audio = []
        all_data = []
        for i in ip_dict2:
            if i.get('port_type') == 'H264' or i.get('port_type') == 'DynamicRTP-Type-96':
                _video.append(i)
            elif i.get('port_type') in audio_coding.values():
                _audio.append(i)
        log.info('_audio:{}\n_video:{}'.format(_audio, _video))
        if _audio == []:
            for __video in _video:
                __v = Deal_dict(__video)
                if __v._type == 'DynamicRTP-Type-96':
                    all_data.append([__v.src_ip, __v.audio_dst_port, __v.dst_ip, __v.audio_src_port])
                if __v._type == 'H264':
                    all_data.append([__v.src_ip, __v.video_dst_port, __v.dst_ip, __v.video_src_port])
        if _video == []:
            for __audio in _audio:
                __a = Deal_dict(__audio)
                if __a._type in audio_coding.values():
                    all_data.append([__a.src_ip, __a.audio_dst_port, __a.dst_ip, __a.audio_src_port, __a._type])
        for __audio in _audio:
            __a = Deal_dict(__audio)
            for __video in _video:
                __v = Deal_dict(__video)
                if __v._type == 'H264':
                    if __v.dst_ip == __a.dst_ip and __v.src_ip == __a.src_ip:
                        if abs(__v.video_dst_port - __a.audio_dst_port) == next_port or abs(
                                __v.video_src_port - __a.audio_src_port) == next_port or abs(
                            __v.video_dst_port - __a.audio_dst_port) == next_bfcp_port or abs(
                            __v.video_src_port - __a.audio_src_port) == next_bfcp_port or abs(
                            __v.video_dst_port - __a.audio_dst_port) == max_port or abs(
                            __v.video_src_port - __a.audio_src_port) == max_port:
                            all_data.append(
                                [__v.dst_ip, __v.video_src_port, __a.audio_src_port, __v.src_ip, __v.video_dst_port,
                                 __a.audio_dst_port, __a._type])
                elif __v._type == 'DynamicRTP-Type-96':
                    all_data.append([__v.src_ip, __v.audio_dst_port, __v.dst_ip, __v.audio_src_port])
        log.info('解析后的ip和端口:{}'.format(all_data))
        return all_data

    ###################################################################################
    """以下是tcp转udp功能代码 暂未整理 功能已实现  split"""
    ###################################################################################

    def merge_pcap(self, sip_pcap, rtp_pcap):
        """合成前提 sip_pcap rtp_pcap内部有序"""
        if not isinstance(sip_pcap, list) or not isinstance(rtp_pcap, list):
            return False
        pcaps = list()
        counter1, counter2 = 0, 0
        while counter1 < len(sip_pcap) and counter2 < len(rtp_pcap):
            if sip_pcap[counter1]['time'] > rtp_pcap[counter2]['time']:
                pcaps.append(rtp_pcap[counter2])
                counter2 += 1
            else:
                pcaps.append(sip_pcap[counter1])
                counter1 += 1
        if counter1 < len(sip_pcap):
            pcaps += sip_pcap[counter1:]
        elif counter2 < len(rtp_pcap):
            pcaps += rtp_pcap[counter2:]
        return pcaps

    def tcp2udp(self, merge_sip=False):
        log.info('正在尝试进行TCP转UDP')
        pcap_path = self.pcap_path
        """用于网络加速下的rtp报文tcp转化udp 会过滤掉除rtp以外的报文 可以选测是否加入sip版问"""
        pcaps = self.handle_pcap(filter_type='tcp', rtp_tcp_mode=True, rtp_data=True)
        if merge_sip:
            sip_pcaps = self.handle_pcap(filter_type='sip')
            pcaps = self.merge_pcap(pcaps, sip_pcaps)
        if not pcaps or len(pcaps) < 100:
            return False
        new_fpcap = open(pcap_path, "wb")
        writer = dpkt.pcap.Writer(new_fpcap)
        if pcaps is not None:
            log.info('tcp转udp成功')
        else:
            log.info('tcp未转成udp，可能是报文不含tcp')
        for pcap in pcaps:
            #print('pcap:{}'.format(pcap))
            eth = pcap['eth']
            if pcap['pcap_type'] == 'rtp':
                udp = dpkt.udp.UDP()
                udp.sport = pcap['udp_sport']
                udp.dport = pcap['udp_dport']
                udp.sum = pcap['udp_sum']
                udp.ulen = pcap['udp_ulen']
                udp.data = pcap['rtp']
                eth.data.p = 17
                eth.data.data = udp
            writer.writepkt(eth, ts=(pcap['time'] - datetime.timedelta(hours=8)).timestamp())
            new_fpcap.flush()
        new_fpcap.close()
        return pcap_path
    
    def __parse_sip_headers(self, sip_obj):
        header_dic = sip_obj.headers
        for result_key in ['authorization', 'www-authenticate', 'authentication-info',
                           'proxy-authenticate', 'proxy-authorization']:
            if header_dic.__contains__(result_key):
                param_dic = dict()
                for param in list(filter(None, re.split(r'[,\s]', header_dic[result_key]))):
                    param_list = param.split('=')
                    if len(param_list) > 1:
                        param_dic[param_list[0]] = param_list[1].strip("\"").strip("sip:")
                header_dic[result_key + '_dic'] = param_dic
        for result_key in ['to', 'from']:
            if "<" in header_dic[result_key]:
                to_list = header_dic[result_key].split("<sip:")
            else:
                to_list = header_dic[result_key].split("sip:")
            param_dic = {
                'display': to_list[0].strip(" ").strip("\""),
                'acc': None if "@" not in header_dic[result_key] else to_list[1].strip(">").split("@")[0],
                'full': to_list[0] if len(to_list) == 1 else to_list[1].split(">")[0]
            }
            header_dic[result_key + '_dic'] = param_dic
        if 'via' in header_dic.keys():
            if type(header_dic['via']) is list:
                for n in range(len(header_dic['via'])):
                    params = list(filter(None, re.split(r'[;\s]', header_dic['via'][n])))
                    if len(params) == 3:
                        param_dic = {
                            'transport': params[0].split('/')[-1],
                            'address': params[1].split(':')[0],
                            'port': params[1].split(':')[1],
                            'branch': params[2].split('=')[-1]
                        }
                    else:
                        param_dic = {
                            'transport': params[0].split('/')[-1],
                            'address': params[1].split(':')[0],
                            'port': params[1].split(':')[1],
                            'rport': '' if params[2].split('=')[-1] == 'rport' else params[2].split('=')[-1],
                            'branch': params[3].split('=')[-1]
                        }
                    via_dic = 'via_dic{}'.format(n + 1)
                    header_dic[via_dic] = param_dic
            else:
                params = list(filter(None, re.split(r'[;\s]', header_dic['via'])))
                param_dic = {
                    'transport': params[0].split('/')[-1],
                    'address': params[1].split(':')[0],
                    'port': params[1].split(':')[1],
                    'rport': '' if params[2].split('=')[-1] == 'rport' else params[2].split('=')[-1],
                    'branch': params[3].split('=')[-1]
                }
                header_dic['via_dic'] = param_dic
        if 'contact' in header_dic.keys() and 'expires=' in header_dic['contact']:
            header_dic['expires'] = header_dic['contact'].split('expires=')[-1]
        return header_dic
    
    def __parse_sip(self, sip_obj):
        def strip_empty(input_list):
            return list(filter(lambda x: x.strip(), input_list))

        result = dict()
        try:
            result.update({
                'sip_method': sip_obj.method,
                'sip_uri': sip_obj.uri,
                'sip_http': 'request'
            })
        except:
            result.update({
                'sip_status': sip_obj.status,
                'sip_reason': sip_obj.reason,
                'sip_http': 'response'
            })
        result.update({
            'sip': sip_obj,
            'sip_headers': self.__parse_sip_headers(sip_obj),
            'sip_version': sip_obj.version
        })
        body_data = sip_obj.data if len(sip_obj.data) > 2 else sip_obj.body
        if body_data == None:
            pass
        elif len(body_data) > 2:
            if b'xml' in body_data:
                return result
            media_attr = dict()
            for attr in strip_empty(body_data.decode("utf-8").split("\r\n"))[::-1]:
                split_list = strip_empty(re.split(r'^([scovtmab])=', attr))
                if len(split_list) == 1 and '=' in split_list[0]:
                    temp_list = split_list[0].split('=')
                    result[temp_list[0].lower()] = temp_list[1]
                elif split_list[0] == 'v':
                    result['sdp_version'] = split_list[1]
                elif split_list[0] == 'o':
                    temp_list = split_list[1].split(' ')
                    result['sdp_owner'] = {
                        'username': temp_list[0],
                        'session_id': temp_list[1],
                        'version': temp_list[2],
                        'network_type': temp_list[3],
                        'address_type': temp_list[4],
                        'address': temp_list[5]
                    }
                elif split_list[0] == 's':
                    result['sdp_session_name'] = split_list[1]
                elif split_list[0] == 'c':
                    temp_list = split_list[1].split(' ')
                    result['sdp_connection_info'] = {
                        'network_type': temp_list[0],
                        'address_type': temp_list[1],
                        'address': temp_list[2]
                    }
                elif split_list[0] == 't':
                    temp_list = split_list[1].split(' ')
                    result['sdp_time'] = {
                        'start': temp_list[0],
                        'stop': temp_list[1]
                    }
                elif split_list[0] == 'a':
                    temp_list = split_list[1].split(':')
                    if temp_list[0] == 'rtpmap':
                        final_list = strip_empty(re.split('[ |/]', temp_list[1]))
                        prepare_dic = {
                            'format': final_list[0],
                            'mime_type': final_list[1],
                            'sample_rate': final_list[2]
                        }
                    elif temp_list[0] == 'fmtp':
                        final_list = strip_empty(re.split('[ |=|;]', temp_list[1]))
                        prepare_dic = {'format': final_list[0]}
                        if len(final_list) == 2:
                            prepare_dic['parameter'] = final_list[1]
                        for c in range(1, len(final_list) - 1, 2):
                            prepare_dic[final_list[c]] = final_list[c + 1]
                    elif len(temp_list) > 1:
                        prepare_dic = ' '.join(temp_list[1:]) if len(temp_list[1:]) > 1 else temp_list[1]
                    else:
                        prepare_dic = None
                    if temp_list[0] not in media_attr.keys():
                        media_attr[temp_list[0]] = prepare_dic
                    elif isinstance(media_attr[temp_list[0]], list):
                        media_attr[temp_list[0]].append(prepare_dic)
                    else:
                        media_attr[temp_list[0]] = [media_attr[temp_list[0]]]
                        media_attr[temp_list[0]].append(prepare_dic)
                elif split_list[0] == 'b':
                    temp_list = split_list[1].split(':')
                    media_attr.update({
                        'bandwidth_modifier': temp_list[0],
                        'bandwidth_value': temp_list[1]
                    })
                elif split_list[0] == "m":
                    temp_list = split_list[1].split(' ')
                    media_attr.update({
                        'media': temp_list[0],
                        'port': temp_list[1],
                        'protocol': temp_list[2],
                        'format': temp_list[3:]
                    })
                    if media_attr['media'] == 'video':
                        if 'content' not in media_attr.keys():
                            result['video_main'] = media_attr
                        elif media_attr['content'] == 'main':
                            result['video_main'] = media_attr
                        elif media_attr['content'] == 'slides':
                            result['video_slides'] = media_attr
                    elif media_attr['media'] == 'audio':
                        result['audio'] = media_attr
                    elif media_attr['media'] == 'application':
                        result['application'] = media_attr
                    media_attr = dict()
                else:
                    if 'sdp_body' not in result.keys():
                        result['sdp_body'] = list()
                    result['sdp_body'].append(split_list)
        return result
    
    def handle_pcap(self, filter_type=None, merge_class=False,
                    rtp_data=False, rtp_stream_type=None, rtp_tcp_mode=False, rtp_strip_fu=False, **kwargs):
        """
        sip 与 rtp 报文 解析， rtp下不包含其携带的音视频数据
        :param rtp_data: 是否保留 rtp 对象 ,False 缩小内存占用
        :param rtp_strip_fu: 是否去掉rtp分片 以帧为单位 仅 rtp 有效 且filter_type默认为rtp rtp_stream_type默认v
        :param rtp_tcp_mode: 是否过滤解析 tcp 协议下的rtp报文 仅 tcp 有效 且filter_type默认为tcp
        :param rtp_stream_type:  获取视频或音频流 仅 rtp 有效
        :param merge_class: 是否用call-id(sip)或ssrc(rtp)组成字典,false则用数组,rtp下stream_type必须指定v或a,否则会混合
        :param filter_type:  sip rtp tcp udp
        :param kwargs:  __read_pcap 传递参数
        :return: 如果是sip报文 且merge_callid 为True则用 call_id为key 每一个call_id中有一个字典列表 其中的字典 key值有

                    keyword         字典中全部key值 字符输出

                    ip              dpkt 类型
                    ip_src ip_dst   源 目标ip (str)
                    ip_mf           是否有分片 (bool)
                    ip_off          分片偏移 (int)
                    ip_protocol     ip协议类型(str) ip_p ip协议编号(int)
                    ip_ttl          ip time to live 值(int)
                    ip_len          ip 长度(int)
                    ip_tos          ip 优先级 (int)
                    ip_sum          ip check_sum (int) 10进制
                    ip_id           ip id (int)

                    eth             dpkt 类型
                    eth_src eth_dst 源 目标 MAC地址(str)
                    eth_type        物理层协议类型

                    time            报文时间戳

                    sip_http        sip的报文类型 request response (str)
                    (request)
                    sip_method      请求方法 (str)
                    sip_uri         请求的目标uri (str)
                    (response)
                    sip_status      sip状态码(str)
                    sip_reason      sip状态说明(str)
                    sip_headers     sip 头内容字典 其中的key有：
                        via/max-forwards/from/to/contact/call-id/cseq/allow
                        /supported/user-agent/content-type/content-length/expires
                        其中to from via 分割后的值存放在 to_idc from_idc via_idc

                    sdp_version         sdp 版本(str)
                    sdp_owner           sdp  [o] 标签 字典 其中的key有：
                        username/session_id/version/network_type/address_type/address
                    sdp_session_name    sdp [s] 标签  sseision name
                    sdp_connection_info sdp [c] 标签 字典 其中key有：
                        network_type/address_type/address
                    sdp_time            sdp [t] 标签 字典 其中 key有：
                        start/stop
                    video_main/video_slides/audio/application 四种属性种类 对应 主流/副流/音频/连接设置 key值有:
                        media/port/protocol/format(list)    [m]标签
                        bandwidth_modifier/bandwidth_value  [b]标签
                        rtpmap                              [a]标签 字典列表 长度不定  key有：
                            format/sample_rate/mime_type
                        fmtp                                [a]标签 字典列表 长度不定  key有：
                            format/字典 键值不定
                        label/confid/userid/setup/floorctrl/connection/content  [a]标签

                如果是rtp报文 且merge_callid 为True则用 ssrc为key 每一个ssrc中有一个字典列表 其中的字典 key值有
                    rtp_nal_nri                 重要性
                    rtp_nal_unit_hdr            报文类型  1 为非IDR帧一般就是P帧 7为SPS 8为PPS 5为I帧 28为FU-A
                    根据rtp_nal_unit_hdr不同 各有key值rtp_p /rtp_sps /rtp_pps /rtp_idr/rtp_fu
                    rtp_sps key值有：
                        profile_idc             档次 66/77/88
                        level_id                码流的Level
                        seq_parameter_set_id    序列参数集的id
                        max_frame_num           frame_num的上限值
                        max_pic_order_cnt       POC 上限
                        num_ref_frames          参考帧的最大数目
                        frame_cropping_flag     是否需要对输出的图像帧进行裁剪
                        frame_mbs_only_flag     宏块的编码方式
                        pic_width               图像的宽度
                        pic_height              图像的高度
                        （其他属性请查看代码）

                    rtp_pps key值有：
                        pic_parameter_set_id
                        seq_parameter_set_id
                        entropy_coding_mode_flag
                        pic_order_present_flag
                        （其他属性请查看代码）

                    rtp_p/rtp_idr key值有：
                        first_mb_in_slice       此片位于一帧的位置
                        slice_type              Slice类型
                        pic_parameter_set_id

                    rtp_fu key值有：
                        start_bit               此包是否是一i帧的开始
                        end_bit                 此包是否是一i帧的结束
                        forbidden_bit
                        nal_unit_type
                        first_mb_in_slice/slice_type/pic_parameter_set_id

        """
        if rtp_tcp_mode:
            filter_type = 'tcp'
        if rtp_strip_fu:
            filter_type = 'rtp'
            rtp_stream_type = 'v'
        coding_list = list(audio_coding.keys()) + list(video_coding.keys())
        if rtp_stream_type is not None:
            if rtp_stream_type in ["v", "video", "视频", "视频流"]:
                coding_list = list(video_coding.keys())
            elif rtp_stream_type in ["a", "audio", "音频", "音频流"]:
                coding_list = list(audio_coding.keys())
        pcap_list = self.__read_pcap(filter_type=filter_type, **kwargs)
        #print('list:{}'.format(pcap_list))
        pcap_info = None
        for pcap in pcap_list:
            result = dict()
            merge_key = None
            for key in ['ip', 'eth', 'time', filter_type]:
                if key not in pcap.keys():
                    continue
            # 基础属性
            value = pcap['ip']
            result.update({
                'ip': value,
                'ip_src': self.op.inet_to_str(value.src),
                'ip_dst': self.op.inet_to_str(value.dst),
                'ip_mf': bool(value.off & dpkt.ip.IP_MF),
                'ip_off': value.off & dpkt.ip.IP_OFFMASK,
                'ip_protocol': protocol_dic[value.p],
                'ip_p': value.p,
                'ip_ttl': value.ttl,
                'ip_len': value.len,
                'ip_tos': value.tos,
                'ip_sum': value.sum,
                'ip_id': value.id,
            })
            try:
                result.update({
                    'protocol_sport': value.data.sport,
                    'protocol_dport': value.data.dport,
                    'protocol_sum': value.data.sum
                })
            except:
                pass
            value = pcap['eth']
            try:
                result.update({
                    'eth': value,
                    'eth_src': self.op.byte2hex(value.src),
                    'eth_dst': self.op.byte2hex(value.dst),
                    'eth_type': protocol_dic[self.op.dec2hex(value.type)],
                })
            except:
                pass
            value = pcap['time']
            result.update({
                'time': value
            })

            value = pcap[filter_type]
            # sip 解析
            if filter_type in ['sip', 'SIP']:
                result.update(self.__parse_sip(value))
                merge_key = result['sip_headers']['call-id']
                result['pcap_type'] = 'sip'
            # rtp 解析
            elif filter_type in ['rtp', 'RTP']:
                parse_result = self.__parse_rtp(value, coding_list, rtp_strip_fu, rtp_data)
                if parse_result:
                    result.update(parse_result)
                else:
                    continue
                merge_key = value.ssrc
                result['pcap_type'] = 'rtp'
            # tcp 解析
            elif filter_type in ['tcp', 'TCP']:
                result.update({
                    'tcp_seq': value.seq,
                    'tcp_ack': value.ack,
                    'tcp_off': value.off,
                    'tcp_flags': value.flags,
                    'tcp_win': value.win,
                    'tcp_urp': value.urp
                })
                result['pcap_type'] = 'tcp'
                # 网络加速模式下 rtp 解析
                #print('2222222')

                if rtp_tcp_mode:
                    #print('111111')

                    if result['ip_dst'] not in media_server_ip and result['ip_src'] not in media_server_ip:
                        continue
                    if len(value.data) < 24:
                        continue
                    udp = dpkt.udp.UDP(value.data[4:])
                    rtp = dpkt.rtp.RTP(udp.data)
                    parse_result = self.__parse_rtp(rtp, coding_list, rtp_strip_fu, rtp_data)
                    if parse_result:
                        result.update({
                            'udp_sport': udp.sport,
                            'udp_dport': udp.dport,
                            'udp_ulen': udp.ulen,
                            'udp_sum': udp.sum
                        })
                        result.update(parse_result)
                    else:
                        continue
                    merge_key = rtp.ssrc
                    result['pcap_type'] = 'rtp'
            # udp 解析
            elif filter_type in ['udp', 'UDP']:
                result.update({
                    'udp_ulen': value.ulen,
                })
                result['pcap_type'] = 'udp'
            # 其他关键字最好直接使用dpkt
            else:
                result['pcap_type'] = 'others'
            # 检查完整
            if 'pcap_type' not in result.keys():
                continue
            # print keyword 关键字 可以查看字典目录
            result['keyword'] = self.keyword_menu(result, result['pcap_type'])

            if merge_class:
                if merge_key is None:
                    continue
                if pcap_info is None:
                    pcap_info = collections.OrderedDict()
                if merge_key not in pcap_info.keys():
                    pcap_info[merge_key] = [result]
                else:
                    pcap_info[merge_key].append(result)
            else:
                if pcap_info is None:
                    pcap_info = list()
                pcap_info.append(result)
        return False if pcap_info is None else pcap_info
    
    def keyword_menu(self, kw, keyword_str=None, header=str()):
        if isinstance(kw, dict):
            header += '\t'
            for k in kw.keys():
                keyword_str += header + '|- ' + str(k) + '(' + str(type(kw[k])).split("'")[1] + ')\n'
                keyword_str = self.keyword_menu(kw[k], keyword_str, header)
        return keyword_str
    
    def __parse_rtp(self, rtp_obj, coding_list, rtp_strip_fu, rtp_data):
        if rtp_obj.data == b'' or rtp_obj.pt not in coding_list:
            return False
        result = {
            'rtp_marker': rtp_obj.m,
            'rtp_p': rtp_obj.p,
            'rtp_x': rtp_obj.x,
            'rtp_timestamp': rtp_obj.ts,
            'rtp_seq': rtp_obj.seq,
            'rtp_pt': rtp_obj.pt,
            'rtp_cc': rtp_obj.cc,
            'rtp_ssrc': rtp_obj.ssrc,
            'rtp_csrc': rtp_obj.csrc,
        }
        if rtp_data:
            result['rtp'] = rtp_obj
        if rtp_obj.pt in video_coding.keys():
            parse_result = self.__parse_rtp_video(rtp_obj, rtp_strip_fu)
            if parse_result:
                result.update(parse_result)
            else:
                return False
        elif rtp_obj.pt in audio_coding.keys() and len(rtp_obj.data) > 2:
            result.update(self.__parse_rtp_audio(rtp_obj))
        else:
            return False
        return result
    
    def __parse_rtp_video(self, rtp_obj, strip_fu=False):
        rtp_data = rtp_obj.data
        result = dict()
        h264 = H264SPSPaser()
        if h264.u(rtp_data, 1, 0) == 1:
            return False
        result['rtp_nal_nri'] = h264.u(rtp_data, 2, h264.getStartBit())
        result['rtp_nal_unit_hdr'] = h264.u(rtp_data, 5, h264.getStartBit())
        if result['rtp_nal_unit_hdr'] in nal_unit_hdr_dic.keys():
            result['rtp_type'] = nal_unit_hdr_dic.get(result['rtp_nal_unit_hdr'])
        else:
            print('rtp_nal_unit_hdr', result['rtp_nal_unit_hdr'], nal_unit_hdr_dic, '\t未收录')
            return False
        pre_idc = dict()
        if result['rtp_nal_unit_hdr'] == 7:
            pre_idc['profile_idc'] = h264.u(rtp_data, 8, h264.getStartBit())
            pre_idc['constraint_set_flag'] = h264.u(rtp_data, 8, h264.getStartBit())
            pre_idc['level_id'] = h264.u(rtp_data, 8, h264.getStartBit())
            pre_idc['seq_parameter_set_id'] = h264.ue(rtp_data, h264.getStartBit())
            if pre_idc['profile_idc'] in [100, 110, 122, 244, 44, 83, 86, 118, 128]:
                pre_idc['chroma_format_idc'] = h264.ue(rtp_data, h264.getStartBit())
                if pre_idc['chroma_format_idc'] == 3:
                    pre_idc['saparate_colour_plane_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
                pre_idc['bit_depth_luma_minus8'] = h264.ue(rtp_data, h264.getStartBit())
                pre_idc['bit_depth_chroma_minus8'] = h264.ue(rtp_data, h264.getStartBit())
                pre_idc['qpprime_y_zero_transform_bypass_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
                pre_idc['seq_scaling_matrix_present_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
                if pre_idc['seq_scaling_matrix_present_flag']:
                    if pre_idc['chroma_format_idc'] == 3:
                        pre_idc['seq_scaling_list_present_flag'] = h264.u(rtp_data, 8, h264.getStartBit())
                    else:
                        pre_idc['seq_scaling_list_present_flag'] = h264.u(rtp_data, 12, h264.getStartBit())
            pre_idc['max_frame_num'] = 2 ** (h264.ue(rtp_data, h264.getStartBit()) + 4)
            pre_idc['pic_order_cnt_type'] = h264.ue(rtp_data, h264.getStartBit())
            if pre_idc['pic_order_cnt_type'] == 0:
                pre_idc['max_pic_order_cnt'] = 2 ** (h264.ue(rtp_data, h264.getStartBit()) + 4)
            else:
                pre_idc['delta_pic_order_always_zero_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
                pre_idc['offset_for_non_nerf_pic'] = h264.se(rtp_data, h264.getStartBit())
                pre_idc['offset_for_top_to_bottom_field'] = h264.se(rtp_data, h264.getStartBit())
                pre_idc['number_ref_frames_in_pic_order_cnt_cycle'] = h264.ue(rtp_data, h264.getStartBit())
                pre_idc['offset_order_frame'] = list()
                for _ in range(pre_idc['number_ref_frames_in_pic_order_cnt_cycle']):
                    pre_idc['offset_order_frame'].append(h264.ue(rtp_data, h264.getStartBit()))
            pre_idc['num_ref_frames'] = h264.ue(rtp_data, h264.getStartBit())
            pre_idc['gaps_in_frame_num_value_allowed_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
            pre_idc['pic_width'] = (h264.ue(rtp_data, h264.getStartBit()) + 1) * 16
            pre_idc['pic_height'] = h264.ue(rtp_data, h264.getStartBit())
            pre_idc['frame_mbs_only_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
            pre_idc['pic_height'] = (pre_idc['pic_height'] + 1) * 16 * (2 - pre_idc['frame_mbs_only_flag'])
            if not pre_idc['frame_mbs_only_flag']:
                pre_idc['mb_adaptive_frame_field_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
            pre_idc['direct_8x8_inference_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
            pre_idc['frame_cropping_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
            if pre_idc['frame_cropping_flag']:
                pre_idc['frame_cropping_left_offset'] = h264.ue(rtp_data, h264.getStartBit())
                pre_idc['frame_cropping_right_offset'] = h264.ue(rtp_data, h264.getStartBit())
                pre_idc['frame_cropping_top_offset'] = h264.ue(rtp_data, h264.getStartBit())
                pre_idc['frame_cropping_bottom_offset'] = h264.ue(rtp_data, h264.getStartBit())
                if pre_idc['chroma_format_idc'] in [1, 2]:
                    crop_unit_x = 2
                else:
                    crop_unit_x = 1
                pre_idc['pic_width'] -= crop_unit_x * (
                        pre_idc['frame_crop_left_offset'] + pre_idc['frame_crop_right_offset'])
                if pre_idc['chroma_format_idc'] == 1:
                    crop_unit_y = 2 * (2 - pre_idc['frame_mbs_only_flag'])
                else:
                    crop_unit_y = 2 - pre_idc['frame_mbs_only_flag']
                pre_idc['pic_height'] -= crop_unit_y * (
                        pre_idc['frame_crop_left_offset'] + pre_idc['frame_crop_right_offset'])
            pre_idc['vui_parameters_present_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
            result['rtp_sps'] = pre_idc
        elif result['rtp_nal_unit_hdr'] == 8:
            pre_idc['pic_parameter_set_id'] = h264.ue(rtp_data, h264.getStartBit())
            pre_idc['seq_parameter_set_id'] = h264.ue(rtp_data, h264.getStartBit())
            pre_idc['entropy_coding_mode_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
            pre_idc['pic_order_present_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
            pre_idc['num_slice_groups_minus1'] = h264.ue(rtp_data, h264.getStartBit())
            if pre_idc['num_slice_groups_minus1'] > 0:
                pre_idc['slice_groups_map_type'] = h264.ue(rtp_data, h264.getStartBit())
                if pre_idc['slice_groups_map_type'] == 0:
                    pre_idc['run_length_minus1'] = list()
                    for _ in range(pre_idc['num_slice_groups_minus1']):
                        pre_idc['run_length_minus1'].append(h264.ue(rtp_data, h264.getStartBit()))
                elif pre_idc['slice_groups_map_type'] == 2:
                    pre_idc['top_left'] = list()
                    pre_idc['bottom_right'] = list()
                    for _ in range(pre_idc['num_slice_groups_minus1']):
                        pre_idc['top_left'].append(h264.ue(rtp_data, h264.getStartBit()))
                        pre_idc['bottom_right'].append(h264.ue(rtp_data, h264.getStartBit()))
                elif pre_idc['slice_groups_map_type'] in [3, 4, 5]:
                    pre_idc['slice_groups_change_direction_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
                    pre_idc['slice_groups_change_rate_flag'].append(h264.ue(rtp_data, h264.getStartBit()))
                elif pre_idc['slice_groups_map_type'] == 6:
                    pre_idc['pic_size_in_map_units_minus1'].append(h264.ue(rtp_data, h264.getStartBit()))
                    pre_idc['slice_group_id'] = list()
                    for _ in range(pre_idc['slice_group_id']):
                        pre_idc['slice_group_id'].append(h264.u(rtp_data, 1, h264.getStartBit()))
            pre_idc['num_ref_idx_l0_active_minus1'] = h264.ue(rtp_data, h264.getStartBit())
            pre_idc['num_ref_idx_l1_active_minus1'] = h264.ue(rtp_data, h264.getStartBit())
            pre_idc['weighted_pred_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
            pre_idc['weighted_bipred_idc'] = h264.u(rtp_data, 2, h264.getStartBit())
            pre_idc['pic_init_qp_minus26'] = h264.se(rtp_data, h264.getStartBit())
            pre_idc['pic_init_qs_minus26'] = h264.se(rtp_data, h264.getStartBit())
            pre_idc['chroma_qp_index_offset'] = h264.se(rtp_data, h264.getStartBit())
            pre_idc['deblocking_filter_control_present_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
            pre_idc['constrained_intra_pred_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
            pre_idc['redundant_pic_cnt_present_flag'] = h264.u(rtp_data, 1, h264.getStartBit())
            result['rtp_pps'] = pre_idc
        elif result['rtp_nal_unit_hdr'] == 1:
            pre_idc['first_mb_in_slice'] = h264.ue(rtp_data, h264.getStartBit())
            pre_idc['slice_type'] = h264.ue(rtp_data, h264.getStartBit())
            pre_idc['pic_parameter_set_id'] = h264.ue(rtp_data, h264.getStartBit())
            result['rtp_p'] = pre_idc
        elif result['rtp_nal_unit_hdr'] == 28:
            pre_idc['start_bit'] = h264.u(rtp_data, 1, h264.getStartBit())
            pre_idc['end_bit'] = h264.u(rtp_data, 1, h264.getStartBit())
            pre_idc['forbidden_bit'] = h264.u(rtp_data, 1, h264.getStartBit())
            pre_idc['nal_unit_type'] = h264.u(rtp_data, 5, h264.getStartBit())
            if pre_idc['start_bit'] == 1:
                pre_idc['first_mb_in_slice'] = h264.ue(rtp_data, h264.getStartBit())
                pre_idc['slice_type'] = h264.ue(rtp_data, h264.getStartBit())
                pre_idc['pic_parameter_set_id'] = h264.ue(rtp_data, h264.getStartBit())
            result['rtp_fu'] = pre_idc
        elif result['rtp_nal_unit_hdr'] == 5:
            pre_idc['first_mb_in_slice'] = h264.ue(rtp_data, h264.getStartBit())
            pre_idc['slice_type'] = h264.ue(rtp_data, h264.getStartBit())
            pre_idc['pic_parameter_set_id'] = h264.ue(rtp_data, h264.getStartBit())
            result['rtp_idr'] = pre_idc
        if strip_fu:
            return self.strip_rtp_fu(result, rtp_obj)
        else:
            return result
    
    def strip_rtp_fu(self, pcap, rtp_obj):
        """过滤掉所有分片"""
        if pcap['rtp_nal_unit_hdr'] == 28:
            fu_dic = pcap.pop('rtp_fu')
            if fu_dic['start_bit'] == 1:
                pre_dic = {
                    'first_mb_in_slice': fu_dic['first_mb_in_slice'],
                    'slice_type': fu_dic['slice_type'],
                    'pic_parameter_set_id': fu_dic['pic_parameter_set_id']
                }
                if fu_dic['slice_type'] == 5:
                    pcap['rtp_type'] = nal_unit_hdr_dic.get(1)
                    pcap['rtp_p'] = pre_dic
                elif fu_dic['slice_type'] == 7:
                    pcap['rtp_type'] = nal_unit_hdr_dic.get(5)
                    pcap['rtp_idr'] = pre_dic
                pcap['rtp_marker'] = 1
            else:
                return False
        elif pcap['rtp_nal_unit_hdr'] == 1 or pcap['rtp_nal_unit_hdr'] == 5:
            if rtp_obj.m != 1:
                return False
            else:
                pcap['first_mb_in_slice'] = 0
        return pcap
    
    def __parse_rtp_audio(self, rtp_obj):
        result = dict()
        rtp_data = rtp_obj.data
        if rtp_obj.pt == 101:  # DTMF RFC2833
            pre_idc = dict()
            hex_num = self.op.byte2hex(rtp_data[:1])
            pre_idc['id'] = str(self.op.hex2dec('0' if hex_num == '' else hex_num))
            if pre_idc['id'] == '10':
                pre_idc['id'] = '*'
            elif pre_idc['id'] == '11':
                pre_idc['id'] = '#'
            bin_str = '{:08d}'.format(int(self.op.hex2bin(str(rtp_data[1]))))
            pre_idc['end'] = bin_str[0]
            pre_idc['reserved'] = bin_str[1]
            pre_idc['volume'] = self.op.bin2dec(bin_str[2:])
            pre_idc['duration'] = self.op.hex2dec(self.op.byte2hex(rtp_data[2:]))
            result['rtp_event'] = pre_idc

        return result
    
    def __read_pcap(self, main_ip=None, server_ip=None, filter_type=None, filter_ip=False, sport=None, dport=None,
                    proto='udp'):
        """读取报文"""
        pcap_name = self.pcap_path
        eth_list = []
        eth_b = 0
        with open(pcap_name, 'rb') as f:
            temp = None
            pcap = dpkt.pcap.Reader(f)
            for timestamp, buf in pcap:
                try:
                    """IP分片前处理"""
                    if eth_b == 0:
                        try:
                            eth = dpkt.ethernet.Ethernet(buf)
                        except:
                            eth_b = 1
                    else:
                        eth = dpkt.sll.SLL(buf)
                    ip = eth.data
                    if isinstance(ip, dpkt.ip.IP):
                        offset = ip.off & dpkt.ip.IP_OFFMASK
                        more_fragment = bool(ip.off & dpkt.ip.IP_MF)
                        if offset != 0 and temp is not None:
                            buf = temp + ip.data
                        if more_fragment:
                            temp = buf
                            continue
                    eth_info = self.___filter_condition(timestamp, buf, main_ip=main_ip, server_ip=server_ip,
                                                       filter_type=filter_type, eth_type=eth_b,
                                                       filter_ip=filter_ip, sport=sport, dport=dport, proto=proto)
                    if not eth_info:
                        continue
                    eth_list.append(eth_info)
                except:
                    continue
            return eth_list

    def ___filter_condition(self, time, buf, main_ip=None, server_ip=None, filter_type=None, filter_ip=False, sport=None,
                           dport=None,
                           proto="udp", eth_type=0):
        # if main_ip == None:
        #     main_ip = self.main_ip
        # else:
        #     main_ip = main_ip
        if eth_type == 0:
            eth = dpkt.ethernet.Ethernet(buf)
        else:
            eth = dpkt.sll.SLL(buf)
        now_date = datetime.datetime.utcfromtimestamp(time) + datetime.timedelta(hours=8)
        ip = eth.data
        if len(buf) > 1514:
            if isinstance(ip.data.data, bytes):
                ip.data.data += buf[1514:]
            elif isinstance(ip.data, bytes):
                ip.data += buf[1514:]
        src_ip = self.op.inet_to_str(ip.src)
        dst_ip = self.op.inet_to_str(ip.dst)
        """对地址的过滤"""
        # if filter_ip == False:  # 对地址过滤
        #     if src_ip == main_ip or dst_ip == main_ip:
        #         if sport != None:
        #             if (src_ip == main_ip and ip.data.sport == sport) or \
        #                     (dst_ip == main_ip and ip.data.dport == sport):
        #                 pass
        #             else:
        #                 return False
        #         pass
        #     else:
        #         return False
        #     if server_ip != None:
        #         if src_ip == server_ip or dst_ip == server_ip:
        #             if dport != None:
        #                 if (src_ip == server_ip and ip.data.sport == dport) or \
        #                         (dst_ip == server_ip and ip.data.dport == dport):
        #                     pass
        #                 else:
        #                     return False
        #             pass
        #         else:
        #             return False
        # else:
        #     if src_ip != main_ip:
        #         return False
        #     if server_ip != None:
        #         if dst_ip != server_ip:
        #             return False
        if proto in ['udp', 'UDP']:
            proto_type = dpkt.udp.UDP
        else:
            proto_type = dpkt.tcp.TCP
        if filter_type != None:  # 对报文类型过滤
            if filter_type in ["tcp", "TCP"]:
                type = dpkt.tcp.TCP
                data = ip.data
            elif filter_type in ["udp", "UDP"]:
                type = dpkt.udp.UDP
                data = ip.data
            elif filter_type in ["rtp", "RTP"]:
                type = proto_type
                data = dpkt.rtp.RTP(ip.data.data)
            elif filter_type in ["ntp", "NTP"]:
                type = proto_type
                data = dpkt.ntp.NTP(ip.data.data)
            elif filter_type in ['http', 'HTTP']:
                type = dpkt.tcp.TCP
                try:
                    data = dpkt.http.Request(ip.data.data)
                except:
                    data = dpkt.http.Response(ip.data.data)
            elif filter_type in ["sip", "SIP"]:
                type = proto_type
                # data = repr(ip.data.data)
                # if "INVITE" in repr(ip.data.data)[0:30] and ip.len == 1500:
                #     data = ip.data.data.decode("utf8")
                # else:
                try:
                    data = dpkt.sip.Request(ip.data.data)
                except:
                    data = dpkt.sip.Response(ip.data.data)
            else:
                type = ip.data
            if not isinstance(ip.data, type):
                return False
        eth_info = {}
        eth_info["time"] = now_date
        eth_info["eth"] = eth
        eth_info["ip"] = ip
        try:
            eth_info[filter_type] = data
            return eth_info
        except:
            return eth_info





if __name__ == "__main__":
    cwd = os.getcwd()
    a = PcapTools("newyuns.pcap", cwd)
    aaa = a.tcp2udp()
    # _path = 'mcu.pcap'
    # with open(_path, 'rb') as f:
    #     packet = dpkt.pcap.Reader(f)
    #     # log.info('解析中.....')
    #     for timestamp, buf in packet:
    #         try:
    #             eth = dpkt.sll.SLL(buf)
    #             print(eth)
    #         except Exception as e:
    #             print(e)
