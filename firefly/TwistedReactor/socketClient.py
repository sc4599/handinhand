# -*- coding: utf-8 -*-
# -*- version: beta-0.0 -*-
####################################################################################################
import socket


####################################################################################################
class Main():
    def __init__(self):
        self.host = '192.168.1.124'
        self.port = 9081

    # --------------------------------------------------------------------------------------------------#
    def Start(self):
        clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSock.connect((self.host, self.port))
        print('connect succeed!')
        while True:
            clientSock.send('doctor:::2222:::aaa/r')
            dataRecv = clientSock.recv(2048)
            if not dataRecv:
                print dataRecv
                break
            elif dataRecv == 'succeed':
                print dataRecv
                break
        clientSock.close()


####################################################################################################
def test():
    m = Main()
    m.Start()


if __name__ == '__main__':
    test()
