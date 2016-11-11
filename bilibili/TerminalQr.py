'''QRCode Terminal Display Helper

'''

import qrcode
import platform
from bilibili.Exceptions import CreateQrException

__all__ = [ 'create' ]

def create(content = None, *, border = 1):
    if (content is None) or (not isinstance(content, str)):
        raise CreateQrException('Terminal display helper need a str type contents')

    qr = qrcode.QRCode(box_size = 1, border = border)
    qr.add_data(content)
    qr.make(fit = True)

    if platform.system() == 'Windows':
        return WindowsMixIn(qr.make_image(), content)
    elif platform.system() == 'Linux':
        return LinuxMixIn(qr.make_image(), content)
    elif platform.system() == 'Darwin':
        return UnixMixIn(qr.make_image(), content)
    else:
        return LinuxMixIn(qr.make_image(), content)

class TerminalQr(object):
    BLACK = '\u2588\u2588'
    BLANK = '  '

    def __init__(self, image, content):
        self.__image     = image
        self.__data      = list(image.getdata())
        self.__pixels    = None
        self.__content   = content
        self.__padding   = 0
        self.__pixelSize = 0

        self.__detect_image_padding()
        self.__split_pixels()

    def reverse(self):
        TerminalQr.BLACK, TerminalQr.BLANK = TerminalQr.BLANK, TerminalQr.BLACK

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is not None:
            raise exc_val

    def __str__(self):
        return self.__generate_terminal_qr()

    def __repr__(self):
        return self.__str__()

    def __generate_terminal_qr(self):
        canvas = ''
        for line in self.__pixels:
            for pixel in line:
                canvas += TerminalQr.BLANK if pixel == 255 else TerminalQr.BLACK
            canvas += '\n'

        return canvas

    def __detect_image_padding(self):
        for x in range(self.__image.width):
            if self.__image.getpixel((x, x)) == 0:
                self.__padding = x
                break

        for x in range(self.__padding, self.__image.width):
            if self.__image.getpixel((x, x)) == 0:
                self.__pixelSize += 1
            else:
                break

    def __split_pixels(self):
        lineSize = self.__image.width + self.__padding * 2
        self.__pixels = [ self.__data[i:i + lineSize] for i in range(0, len(self.__data), lineSize) ]


class WindowsMixIn(TerminalQr):
    pass

class LinuxMixIn(TerminalQr):
    BLACK = 'MM'
    BLANK = '  '

class UnixMixIn(TerminalQr):
    BLACK = 'MM'
    BLANK = '  '
