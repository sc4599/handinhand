# # -*- coding: gbk -*-
# #2010-3-25
# #python 测试与应用:41357415
# #深圳IT招聘求职：105095215
# #武冈深圳高级群：66250781
# #程序针对ip.txt中的ip，ssh上去执行命令，取回执行结果，写入本地文件
# #存在问题：执行一个命令需要ssh一次。执行命令中的大括号不知如何处理。
# #另外有些正则表达式也可以使用cut之类的命令来替换
# #gtalk： xurongzhong#gmail.com
#
# # import pexpect
# import sys
# import re
# import os
# import time
#
#
# #设定字符编码为GBK
# reload(sys)
# sys.setdefaultencoding('gbk')
#
# def ssh_command(ip, command):
#     """
#     登录到一台机器执行执行的命令，取回返回结果
#     """
#     ssh_newkey = 'Are you sure you want to continue connecting'
#     # 为 ssh 命令生成一个 spawn 类的子程序对象.
#     child = pexpect.spawn('ssh -q -p 36000 soso_plt@'+ip + " " +  command)
#     i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
#     # 如果登录超时，打印出错信息，并退出.
#     if i == 0: # Timeout
#         print 'ERROR!'
#         print 'SSH could not login. Here is what SSH said:'
#         print child.before, child.after
#         return None
#     # 如果 ssh 没有 public key，接受它.
#     if i == 1: # SSH does not have the public key. Just accept it.
#         child.sendline ('yes')
#         child.expect ('password: ')
#         i = child.expect([pexpect.TIMEOUT, 'password: '])
#         if i == 0: # Timeout
#             print 'ERROR!'
#             print 'SSH could not login. Here is what SSH said:'
#             print child.before, child.after
#             return None
#     # 输入密码.
#     child.sendline("!plat@soso")
#     return child
#
# def process_info(Pr_name):
#     #获取drm_processes 的进程号
#     cmd = r"ps aux  | grep " + Pr_name + r" | grep -v grep"
#     child = ssh_command(ip,cmd)
#     child.expect(pexpect.EOF)
#     processes = child.before
#     processes_num = re.findall('soso_plt.*?(\d+) ', processes)
#     f_out.write("\n\n" + Pr_name +  "  的进程信息:")
#     if not  processes_num:
#         f_out.write("\nThere is NO " + Pr_name + " running"  )
#     else:
#         for pid in processes_num:
#             f_out.write("\n****"+ pid)
#             #获取进程的CPU和内存使用率
#             cmd = 'top -p' + pid + ' -b -n1 | tail -n2 | head -n1'
#             child = ssh_command(ip,cmd)
#             child.expect(pexpect.EOF)
#             info = child.before
#             info = info.split()
#             cpu = info[8]
#             mem= info[9]
#
#             #获取句柄数
#             cmd = 'ls -l /proc/' + pid + '/fd |wc -l '
#             child = ssh_command(ip,cmd)
#             child.expect(pexpect.EOF)
#             handle = child.before.strip()
#
#             f_out.write("\n********CPU占用率:"+ cpu + "****内存占用率:" + mem + "****句柄:" + handle)
#
# def cpu_info():
#     #获取CPU数目
#     child = ssh_command (ip , "cat /proc/cpuinfo " )
#     child.expect(pexpect.EOF)
#     cpuinfo = child.before
#     cpu_num = re.findall('processor.*?(\d+)', cpuinfo)[-1]
#     cpu_num = str(int(cpu_num) + 1 )
#     f_out.write("\nCPU number:" + cpu_num )
#
#
#
# def mem_info():
#     #获取内存信息
#     child = ssh_command(ip,"cat /proc/meminfo  ")
#     child.expect(pexpect.EOF)
#     meminfo = child.before
#     mem_values = re.findall('(\d+)\ kB', meminfo)
#
#     MemTotal = mem_values[0]
#     MemFree = mem_values[1]
#     Buffers = mem_values[2]
#     Cached = mem_values[3]
#     SwapCached = mem_values[4]
#     Active = mem_values[5]
#     Inactive = mem_values[6]
#     HighTotal = mem_values[7]
#     HighFree = mem_values[8]
#     LowTotal = mem_values[9]
#     LowFree = mem_values[10]
#     SwapTotal = mem_values[11]
#     SwapFree = mem_values[12]
#     Dirty = mem_values[13]
#     Writeback= mem_values[14]
#     AnonPages = mem_values[15]
#     Mapped = mem_values[16]
#     Slab = mem_values[17]
#     CommitLimit = mem_values[18]
#     Committed_AS = mem_values[19]
#     PageTables = mem_values[20]
#     VmallocTotal = mem_values[21]
#     VmallocUsed = mem_values[22]
#     VmallocChunk = mem_values[23]
#     Hugepagesize = mem_values[-1]
#
#     #计算内存使用比率
#     Free_Mem = int(MemFree) + int(Buffers)  + int(Cached)
#     Used_Mem = int(MemTotal) - Free_Mem
#     Rate_Mem = Used_Mem/float(MemTotal)
#
#     f_out.write("\nMEM number:" + MemTotal )
#     f_out.write("\nMEM Free:" + str(Free_Mem) )
#     f_out.write("\nMEM Used:" + str(Used_Mem) )
#     f_out.write("\nMEM Usage:" + str(Rate_Mem) )
#
#     #计算交换内存使用比率
#     Rate_Swap = 1 - int(SwapFree)/float(SwapTotal)
#     f_out.write("\nSwapTotal:" + SwapTotal )
#     f_out.write("\nSwapFree:" + SwapFree )
#     f_out.write("\nSwap Usage:" + str(Rate_Swap) )
#
# def vmstat_info():
#     #获取CPU数目
#     child = ssh_command (ip , "vmstat 1 2 | tail -n 1" )
#     child.expect(pexpect.EOF)
#     vmstat_info = child.before.strip().split()
#     processes_waiting =  vmstat_info[0]
#     processes_sleep = vmstat_info[1]
#     io_bi = vmstat_info[8]
#     io_bo = vmstat_info[9]
#     System_in = vmstat_info[10]
#     System_cs = vmstat_info[11]
#     cpu_us = vmstat_info[12]
#     cpu_sy = vmstat_info[13]
#     cpu_id = vmstat_info[14]
#     cpu_wa = vmstat_info[15]
#     cpu_st = vmstat_info[16]
#
#     f_out.write("\nprocesses_waiting:" + processes_waiting )
#     f_out.write("\nprocesses_sleep:" + processes_sleep )
#     f_out.write("\nio_bi:" + io_bi )
#     f_out.write("\nio_bo:" + io_bo )
#     f_out.write("\nSystem_in:" + System_in )
#     f_out.write("\nSystem_cs :" + System_cs )
#     f_out.write("\ncpu_us:" + cpu_us )
#     f_out.write("\ncpu_sy:" + cpu_sy )
#     f_out.write("\ncpu_id:" + cpu_id )
#     f_out.write("\ncpu_wa:" + cpu_wa )
#     f_out.write("\ncpu_st:" + cpu_st )
#
# #打开日志文件
# Pr_name = sys.argv[1]
# time_now = time.strftime("%Y-%m-%d_%H-%M-%S-",time.localtime())
# filename = time_now + Pr_name + ".log"
# f_out = open(filename,'w')
# #对每个ip的信息进行监控
# for ip in open("ip.txt"):
#     ip = ip.strip()
#     f_out.write("\n" + "*"*80+"\n\n"+ip)
#
#     cpu_info()
#     mem_info()
#     vmstat_info()
#
#     #获取top中的cpu空闲率
#     child = ssh_command(ip,"top -b -n 1")
#     child.expect(pexpect.EOF)
#     top = child.before
#     idle_cpu = re.search(',\ (\d+.*?)%id', top).group(1)
#     f_out.write("\nCPU IDLE:" + idle_cpu )
#
#     process_info(Pr_name)