''' BiliBili Live Package

'''

import struct
import socket
from BLiH import Config, Exceptions

# Package Type None
PKG_TYPE_NONE = -1

# Package Type Value
PKG_TYPE_JOIN_ROOM = 7

# Package Type Value
PKG_TYPE_HEARTBEAT = 2

def sendPackage(sock, package):
    length = len(package)
    while length > 0:
        length -= sock.send(package)

    return True

def receivePackage(sock, *, receiveMaxLength = 4096):
    buffer = sock.recv(4)
    packageLength, = struct.unpack('!I', buffer)
    packageLength -= 4

    while packageLength > 0:
        buffer += sock.recv(min(receiveMaxLength, packageLength))
        packageLength -= len(buffer)

    return buffer

''' Response Format

    packageLength Int(4)
    unknown field Short(2)
    unknown field Short(2)
    package type  Int(4)
    unknown field Int(4)
    json data     0+
'''
class LivePackageParser(object):

    def __init__(self):
        pass

class LivePackageGenerator(object):

    # Package Header Length = Int(4) + Short(2) + Short(2) + Int(4) + Int(4) + Int(4) = 16
    __PKG_HEADER_LENGTH = 16

    # Package API Version
    __PKG_API_VERSION = 1

    # Unknown Field, Pad Field
    __UNKNOWN_FIELD_VALUE = 1

    # Join Room Package Body Format
    __JOIN_ROOM_BODY_FORMAT = '{ "roomid": %s, "uid": %s }'

    # DanMu Server Address
    __DM_SERVER_ADDRESS = 'dm.live.bilibili.com'

    # DanMu Server Port
    __DM_SEVER_PORT = 788

    def __init__(self, sock = None):
        if sock is not None and isinstance(sock, int):
            self.__sock = sock
        else:
            try:
                self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__sock.connect((self.__DM_SERVER_ADDRESS, self.__DM_SEVER_PORT))
            except Exception as e:
                print('LivePackageGenerator::__init__() error', e)

    def join(self, roomId, uid):
        data    = (self.__JOIN_ROOM_BODY_FORMAT % (roomId, uid)).encode(Config.ENCODING)
        package = self.__packageGenerator(type = PKG_TYPE_JOIN_ROOM, body = data)

        if sendPackage(self.__sock, package) is True:
            response = receivePackage(self.__sock)
            print(response)
            if response == b'\x00\x00\x00\x10\x00\x10\x00\x01\x00\x00\x00\x08\x00\x00\x00\x01':
                response = receivePackage(self.__sock)
                print(response)
                return True

    def heartbeat(self):
        pass

    def __packageGenerator(self, *, type = PKG_TYPE_HEARTBEAT, body = None):
        if type not in (PKG_TYPE_HEARTBEAT, PKG_TYPE_JOIN_ROOM):
            pass

        if isinstance(body, str):
            body = body.encode(Config.ENCODING)
        if body is not None and not isinstance(body, bytes):
            raise TypeError('LivePackageGenerator::___makePackage params error')

        return self.___createPackage(type = type, body = body)

    def ___createPackage(self, *, pkgLength = 0, headerLength = __PKG_HEADER_LENGTH,
                         version = __PKG_API_VERSION, type = 0, unknown = __UNKNOWN_FIELD_VALUE, body = None):
        if isinstance(body, str):
            body = body.encode(Config.ENCODING)

        if body is not None and not isinstance(body, bytes):
            raise TypeError('LivePackageGenerator::___makePackage params error')

        pkgLength = headerLength + len(body)

        try:
            if body is None:
                return struct.pack('!IHHII', pkgLength, headerLength, version, type, unknown)
            return struct.pack('!IHHII{}s'.format(len(body)), pkgLength, headerLength, version, type, unknown, body)
        except Exception as e:
            pass