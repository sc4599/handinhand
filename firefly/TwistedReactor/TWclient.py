# -*- coding: UTF-8 -*-

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet import reactor
import random
import string


class Game(LineOnlyReceiver):
    def lineReceived(self, data):
        self.factory.sendAll("%s" % (data))

    def getId(self):
        return str(self.transport.getPeer())

    def connectionMade(self):
        print "New User Login:", self.getId()
        self.transport.write("welcome to handinhand!\n")
        self.factory.addClient(self)

    def connectionLost(self, reason):
        self.factory.delClient(self)


class GameFactory(Factory):
    protocol = Game

    def __init__(self):
        self.clients = []
        self.player = []
        self.msg = ''
        self.x = range(100, 700)
        self.y = range(100, 500)

    def getPlayerId(self):
        return len(self.player)

    def addClient(self, newclient):
        self.clients.append(newclient)

    def delClient(self, client):
        self.clients.remove(client)

    def sendAll(self, data):
        print 'sendAll data=%s'%data
        if data.find('<policy-file-request/>') != -1:
            self.transport.write(
                '<cross-domain-policy><allow-access-from domain="127.0.0.1" to-ports="*"/></cross-domain-policy>\0')
        elif data.find(':') != -1:
            print data
            arr = data.split(':')
            prefix = arr[0]
            content = arr[1]
            if prefix.find('player') != -1:
                newPlayer = [content, str(random.randrange(200, 600)), str(random.randrange(150, 350)),
                             str(random.randrange(1, 5))]
                self.player.append(newPlayer)
                self.msg = ' player ' + content + ' come to game!'
                # 广播所有玩家的位置
                temp = []
                playerData = ':::'
                for pos in self.player:
                    temp.append(string.join(pos, '---'))
                playerData = playerData + string.join(temp, '***')
                for proto in self.clients:
                    proto.transport.write('[system]: ' + self.msg + '\n')
                    proto.transport.write(playerData)
            elif prefix.find('pos') != -1:
                playerName, x, y = content.split('---')
                i = 0
                for p in self.player:
                    if p[0] == playerName:
                        p[1] = x
                        p[2] = y
                for proto in self.clients:
                    proto.transport.write(data)
            else:
                self.msg = data
                for proto in self.clients:
                    proto.transport.write(self.msg + '\n')
        else:
            pass


gggggg = GameFactory()

from twisted.web import server, resource, static
from twisted.internet import reactor


class Simple(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("", self)
        self.putChild("static", static.File("ar/wwwdocs"))

    def render_GET(self, request):
        # gggggg.sendAll(request)
        gggggg.sendAll('player:2222')
        print request
        return "Hello, world!"


reactor.listenTCP(8006, gggggg)
reactor.listenTCP(8080, server.Site(Simple()))

reactor.run()
