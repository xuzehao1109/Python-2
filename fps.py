# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2020.11.27
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""
import datetime
import socket

import dpkt

a={104: "H264",105: "H264",106: "H264",107: "H264",108: "H264",109: "H264",110: "H264"}
path='测试报文-VT50V1-双方辅流.cap'
def get_fps():
    frame_rate_list = []
    mark_n=0
    frame_rate_time_list = []
    with open(path,'rb') as f:
        if '.pcapng' in path:
            packet = dpkt.pcapng.Reader(f)
            # 兼容pacpng格式报文
        else:
            packet = dpkt.pcap.Reader(f)
        print('解析中.....')
        n=0
        for timestamp, buf in packet:
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            now_time=datetime.datetime.utcfromtimestamp(timestamp) + datetime.timedelta(hours=8)
            try:
                src_port = ip.data.sport
                dst_port = ip.data.dport
                rtp = dpkt.rtp.RTP(ip.data.data)
                if rtp.pt not in a.keys():
                    continue
                print(src_port,dst_port)
                if (src_port==50046 and dst_port==35698) or (src_port==35698 and dst_port==50046):
                    mark=rtp.m
                    #print(mark)
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
                        print(old,mark_n)

                        mark_n = 1

            except:
                pass

    frame_rate_len = []
    for rate_len in range(1, len(frame_rate_list)+1):
        frame_rate_len.append(rate_len)
    min_frame_rate = min(frame_rate_list)
    max_frame_rate = max(frame_rate_list)
    avg_frame_rate = int(sum(frame_rate_list)/len(frame_rate_list))
    total_frame_rate = sum(frame_rate_list)
    min_frame_rate_time = frame_rate_time_list[frame_rate_list.index(min_frame_rate)]
    max_frame_rate_time = frame_rate_time_list[frame_rate_list.index(max_frame_rate)]
    print("最小帧率（对应的时间）:", min_frame_rate, "(time:",min_frame_rate_time , ")")
    print("最大帧率（对应的时间）:", max_frame_rate, "(time:", max_frame_rate_time, ")")
    print("平均帧率:", avg_frame_rate)
    print("总帧数：", sum(frame_rate_list))

if __name__ == '__main__':

    #get_fps()
    with open(path,'rb') as f:
        if '.pcapng' in path:
            packet = dpkt.pcapng.Reader(f)
            # 兼容pacpng格式报文
        else:
            packet = dpkt.pcap.Reader(f)
        print('解析中.....')
        n=0
        for timestamp, buf in packet:
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            now_time=datetime.datetime.utcfromtimestamp(timestamp) + datetime.timedelta(hours=8)
            try:
                rtp = dpkt.rtp.RTP(ip.data.data)
                print(rtp.seq)
            except:
                pass