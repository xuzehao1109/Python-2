# -*- coding: utf-8 -*-
"""
__version__ = '1.0'

Created on 2020.11.30
Author xuzehao

Copyright (c) 2020 Star-Net
模块注释:
"""
import math
import re
import socket
import subprocess

base = [str(x) for x in range(10)] + [chr(x) for x in range(ord('A'), ord('A') + 6)]


class Operation(object):
    startBit = 0

    """==========字节，字体等转换部分=========="""

    def inet_to_str(self, inet):
        """Convert inet object to a string

            Args:
                inet (inet struct): inet network address
            Returns:
                str: Printable/readable IP address
        """
        # First try ipv4 and then ipv6
        try:
            return socket.inet_ntop(socket.AF_INET, inet)
        except ValueError:
            return (socket.inet_ntop(socket.AF_INET6, inet))

    def bin2text(self, string_num):
        string_num = str(string_num)
        while len(string_num) < 8:
            string_num = "0" + string_num
        return string_num

    def byte2bin(self, byte_num):
        dec_num = int.from_bytes(byte_num, byteorder='big', signed=False)  # 将字节转为10进制
        bin_num = self.dec2bin(dec_num)  # 10进制转为2进制
        if bin_num == "":
            bin_num = "0"
        return bin_num

    def byte2dec(self, byte_num):
        dec_num = int.from_bytes(byte_num, byteorder='big', signed=False)  # 将字节转为10进制
        return dec_num

    def byte2hex(self, byte_num):
        """字节转16进制"""
        dec_num = self.byte2dec(byte_num)
        hex_num = self.dec2hex(dec_num)
        return hex_num

    def hex2byte(self, str_hex):
        byte_num = bytes().fromhex(str_hex)
        return byte_num

    # bin2dec
    # 二进制 to 十进制: int(str,n=10)
    def bin2dec(self, string_num):
        return str(int(string_num, 2))

    # hex2dec
    # 十六进制 to 十进制
    def hex2dec(self, string_num):
        return str(int(string_num.upper(), 16))

    # dec2bin
    # 十进制 to 二进制: bin()
    def dec2bin(self, string_num):
        num = int(string_num)
        mid = []
        while True:
            if num == 0: break
            num, rem = divmod(num, 2)
            mid.append(base[rem])

        return ''.join([str(x) for x in mid[::-1]])

    # dec2hex
    # 十进制 to 八进制: oct()
    # 十进制 to 十六进制: hex()
    def dec2hex(self, string_num):
        num = int(string_num)
        mid = []
        while True:
            if num == 0: break
            num, rem = divmod(num, 16)
            mid.append(base[rem])

        return ''.join([str(x) for x in mid[::-1]])

    # hex2tobin
    # 十六进制 to 二进制: bin(int(str,16))
    def hex2bin(self, string_num):
        return self.dec2bin(self.hex2dec(string_num.upper()))

    # bin2hex
    # 二进制 to 十六进制: hex(int(str,2))
    def bin2hex(self, string_num):
        return self.dec2hex(self.bin2dec(string_num))

    def time2itv(self, sTime):
        """时间转为秒数03:45:03.248630 =》13503.248630"""
        p = "^([0-9]+):([0-5][0-9]):([0-5][0-9]).([0-9]+)$"
        cp = re.compile(p)
        try:
            mTime = cp.match(sTime)
        except TypeError:
            return "[InModuleError]:time2itv(sTime) invalid argument type"
        if mTime:
            t = list(map(int, mTime.group(1, 2, 3)))
            ms = "0." + mTime.group(4)
            return 3600 * t[0] + 60 * t[1] + t[2] + float(ms)
        else:
            return "[InModuleError]:time2itv(sTime) invalid argument value"

    def list2haxi(self, list_info):
        dicts = dict(zip(list_info, list_info))
        return dicts

    def get_count_time_len(self, forward, next):
        """计算时间差，以毫秒为单位"""
        if (next - forward).seconds == 0:
            time_len = ((next - forward).microseconds) / 1000
        else:
            tims_s = ((next - forward).seconds) * 1000
            tims_m = ((next - forward).microseconds) / 1000
            time_len = tims_s + tims_m
        return time_len

    def count_duplicated(self, info_list):
        """计算重复个数"""
        info_dict = {}
        b = set(info_list)
        for each_b in b:
            count = 0
            for each_a in info_list:
                if each_b == each_a:
                    count += 1
            info_dict[each_b] = count
        return info_dict

    def count_tmmbr_info(self, data):
        """计算tmmbr字段转换"""
        tmmbr_data = self.byte2bin(data[16:19])
        for n in range(24 - len(tmmbr_data)):
            tmmbr_data = "0" + tmmbr_data
        exp = self.bin2dec(tmmbr_data[0:6])
        mantissa = int(int(self.bin2dec(tmmbr_data[6:])) / 2)
        info = "{}*2^{}".format(mantissa, exp)
        return info

    def count_nack_info(self, data):
        """计算nack的数量"""
        loss_list = []
        nack_data = data[12:]
        for i in range(0, len(nack_data), 4):
            nack_bin = self.byte2bin(nack_data[i:i + 2])
            PID = self.bin2dec(nack_bin)
            BLP = self.byte2bin(nack_data[i + 2:i + 4])
            loss_list.append(int(PID))
            if BLP != "0000":
                for n in range(1, len(BLP) + 1):
                    loss_list.append(int(PID) + n)
        return loss_list

    def judge_file(self, file, path):
        """判断文件是否存在"""
        ls_dir = subprocess.check_output("ls {}".format(path), shell=True).decode('utf-8')
        if file in ls_dir:
            return True
        return False

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
