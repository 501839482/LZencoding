# -*- coding: UTF-8 -*-
import math
import struct
import time

def read(filename):
    #读取文件并以二进制形式存储返回
    t0 = time.time()  # 用于记录时间

    with open(filename, mode='rb') as f:
        r = f.read()
        r_ = ''
        for i in r:
            r_ = r_ + (bin(i))[2:].zfill(8)     #'rb'方式读出的是ascii，将其转为比特串（去掉头部的'0b'标识）并填满8位。

    t1 = time.time()
    print('读取完成     耗时%0.5f     文件大小%d bit' % ((t1 - t0), len(r_)))
    return r_

def encoder(r):
    #对文件比特串进行LZ编码
    t0 = time.time()    #用于记录时间

    dict = {}           #编码过程字典
    id = 0              #段号
    code = []           #保存每一段的编码结果(比特串构成的列表)
    result_bin = ''     #保存编码后的比特串

    while(len(r)>0):
        code_id = 0
        flag_match = 1

        # 从头选取不在字典中的短语
        for i in range(1, len(r) + 1):
            phrase = r[0:i]             #记录短语
            if phrase not in dict:
                flag_match = 0
                break
            else:
                code_id = dict[phrase]  #记录其前n-1个字符对应的段号

        # 当剩余字符与字典中短语完全匹配时，直接用段号进行编码（仅用于处理文件末尾的编码）
        if flag_match == 1:
            code.append(code[dict[phrase] - 1])
            break

        #记录短语的最后一个字符
        if phrase[-1] == '0':
            code_last = '0'
        else:
            code_last = '1'

        #对短语进行编码（段号+尾符号）并加入列表
        id = id + 1
        dict[phrase] = id
        code.append(bin(code_id)[2:].zfill(math.ceil(math.log2(id))) + code_last)
        r = r[len(phrase):]     #从原始比特串删除已完成编码的短语

    #将比特串列表转换为比特串，即最终编码结果
    for i in code:
        result_bin = result_bin + i

    #编码结束，返回编码结果和字典长度
    t1 = time.time()
    print('编码完成     耗时%0.5f' % (t1 - t0))
    return result_bin,len(dict)

def decoder(code_bin, size):
    #对LZ编码后的比特串进行译码
    t0 = time.time()        # 用于记录时间

    dict = {'':''}          #译码过程字典
    original_code = ['']    #保存每一段的译码结果(比特串构成的列表)
    original_bin = ''       #保存译码后的比特串
    num = 0

    while len(code_bin) > 0:
        length = max(math.ceil(math.log2(len(dict))) + 1, 2)
        code_ = code_bin[0:length]

        #如果段号为0，则直接在译码结果列表中加入尾符号，同时更新字典
        if code_[0:length-1] == '0':
            original_code.append(code_[-1])
            num = num + 1
            dict[code_] = original_code[num]
        else:
            #如果未达到编码字典大小，则以 段号+尾符号 的形式进行译码
            if num < size:
                original_code.append(original_code[int(code_[0:length-1],2)] + code_[-1])
                num = num + 1
                dict[code_] = original_code[num]
            else:
            #如果达到编码字典大小，则直接匹配段号
                original_code.append(dict[code_])
        code_bin = code_bin[length:]

    # 将比特串列表转换为比特串，即最终译码结果
    for i in original_code:
        original_bin = original_bin + i

    #译码结束，返回译码结果
    t1 = time.time()
    print('译码完成     耗时%0.5f' % (t1 - t0))
    return original_bin

def write(filename, text_bin):
    #将比特串写入文件，并转换为中文字符
    t0 = time.time()  # 用于记录时间

    filesize = len(text_bin)
    text = []   #对比特串每八位分割（保证以ascii为单位写回）形成的列表

    #将比特串转换为ascii
    while len(text_bin) > 0:
        text.append(int(text_bin[0:8],2))
        text_bin = text_bin[8:]

    #以比特流（二进制）形式写入译码文件
    with open(filename,'wb') as f:
        while len(text) > 0:
            f.write(struct.pack('B',text[0]))
            text = text[1:]

    t1 = time.time()
    print('写入完成     耗时%0.5f     文件大小%d bit' % ((t1 - t0), filesize))
    return

def LZ(filename):
    #LZ编码完整过程

    r = read(filename)                  #读取
    code = encoder(r)                   #编码
    write('编码结果'+filename, code[0])  #编码后文件写入
    r_ = decoder(code[0],code[1])       #译码
    write('译码结果'+filename,r_)        #姨妈后文件写入

def main():
    print('---------------------------------------------------')
    LZ('诺贝尔化学奖.txt')
    print('---------------------------------------------------')
    LZ('脑机接口新突破.docx')
    print('---------------------------------------------------')

if __name__ == '__main__':
    main()
