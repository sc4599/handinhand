# # -*- coding: gbk -*-
# #2010-3-25
# #python ������Ӧ��:41357415
# #����IT��Ƹ��ְ��105095215
# #������ڸ߼�Ⱥ��66250781
# #�������ip.txt�е�ip��ssh��ȥִ�����ȡ��ִ�н����д�뱾���ļ�
# #�������⣺ִ��һ��������Ҫsshһ�Ρ�ִ�������еĴ����Ų�֪��δ���
# #������Щ������ʽҲ����ʹ��cut֮����������滻
# #gtalk�� xurongzhong#gmail.com
#
# # import pexpect
# import sys
# import re
# import os
# import time
#
#
# #�趨�ַ�����ΪGBK
# reload(sys)
# sys.setdefaultencoding('gbk')
#
# def ssh_command(ip, command):
#     """
#     ��¼��һ̨����ִ��ִ�е����ȡ�ط��ؽ��
#     """
#     ssh_newkey = 'Are you sure you want to continue connecting'
#     # Ϊ ssh ��������һ�� spawn ����ӳ������.
#     child = pexpect.spawn('ssh -q -p 36000 soso_plt@'+ip + " " +  command)
#     i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
#     # �����¼��ʱ����ӡ������Ϣ�����˳�.
#     if i == 0: # Timeout
#         print 'ERROR!'
#         print 'SSH could not login. Here is what SSH said:'
#         print child.before, child.after
#         return None
#     # ��� ssh û�� public key��������.
#     if i == 1: # SSH does not have the public key. Just accept it.
#         child.sendline ('yes')
#         child.expect ('password: ')
#         i = child.expect([pexpect.TIMEOUT, 'password: '])
#         if i == 0: # Timeout
#             print 'ERROR!'
#             print 'SSH could not login. Here is what SSH said:'
#             print child.before, child.after
#             return None
#     # ��������.
#     child.sendline("!plat@soso")
#     return child
#
# def process_info(Pr_name):
#     #��ȡdrm_processes �Ľ��̺�
#     cmd = r"ps aux  | grep " + Pr_name + r" | grep -v grep"
#     child = ssh_command(ip,cmd)
#     child.expect(pexpect.EOF)
#     processes = child.before
#     processes_num = re.findall('soso_plt.*?(\d+) ', processes)
#     f_out.write("\n\n" + Pr_name +  "  �Ľ�����Ϣ:")
#     if not  processes_num:
#         f_out.write("\nThere is NO " + Pr_name + " running"  )
#     else:
#         for pid in processes_num:
#             f_out.write("\n****"+ pid)
#             #��ȡ���̵�CPU���ڴ�ʹ����
#             cmd = 'top -p' + pid + ' -b -n1 | tail -n2 | head -n1'
#             child = ssh_command(ip,cmd)
#             child.expect(pexpect.EOF)
#             info = child.before
#             info = info.split()
#             cpu = info[8]
#             mem= info[9]
#
#             #��ȡ�����
#             cmd = 'ls -l /proc/' + pid + '/fd |wc -l '
#             child = ssh_command(ip,cmd)
#             child.expect(pexpect.EOF)
#             handle = child.before.strip()
#
#             f_out.write("\n********CPUռ����:"+ cpu + "****�ڴ�ռ����:" + mem + "****���:" + handle)
#
# def cpu_info():
#     #��ȡCPU��Ŀ
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
#     #��ȡ�ڴ���Ϣ
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
#     #�����ڴ�ʹ�ñ���
#     Free_Mem = int(MemFree) + int(Buffers)  + int(Cached)
#     Used_Mem = int(MemTotal) - Free_Mem
#     Rate_Mem = Used_Mem/float(MemTotal)
#
#     f_out.write("\nMEM number:" + MemTotal )
#     f_out.write("\nMEM Free:" + str(Free_Mem) )
#     f_out.write("\nMEM Used:" + str(Used_Mem) )
#     f_out.write("\nMEM Usage:" + str(Rate_Mem) )
#
#     #���㽻���ڴ�ʹ�ñ���
#     Rate_Swap = 1 - int(SwapFree)/float(SwapTotal)
#     f_out.write("\nSwapTotal:" + SwapTotal )
#     f_out.write("\nSwapFree:" + SwapFree )
#     f_out.write("\nSwap Usage:" + str(Rate_Swap) )
#
# def vmstat_info():
#     #��ȡCPU��Ŀ
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
# #����־�ļ�
# Pr_name = sys.argv[1]
# time_now = time.strftime("%Y-%m-%d_%H-%M-%S-",time.localtime())
# filename = time_now + Pr_name + ".log"
# f_out = open(filename,'w')
# #��ÿ��ip����Ϣ���м��
# for ip in open("ip.txt"):
#     ip = ip.strip()
#     f_out.write("\n" + "*"*80+"\n\n"+ip)
#
#     cpu_info()
#     mem_info()
#     vmstat_info()
#
#     #��ȡtop�е�cpu������
#     child = ssh_command(ip,"top -b -n 1")
#     child.expect(pexpect.EOF)
#     top = child.before
#     idle_cpu = re.search(',\ (\d+.*?)%id', top).group(1)
#     f_out.write("\nCPU IDLE:" + idle_cpu )
#
#     process_info(Pr_name)