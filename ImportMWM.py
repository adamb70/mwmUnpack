from struct import *

from utils import BinaryStream
from TagReaders import TagReaders

#import pyassimp


def LoadOldVersion(stream):
    print('old version not implemented')
    raise Exception


def LoadTagData(stream):
    retTagData = {}
    key = stream.readString7()

    array = []
    for i in range(stream.readInt32()):
        array.append(stream.readString7())
    retTagData[key] = array

    if len(array) > 0 and array[0].startswith('Version:'):
        version = int(array[0].replace('Version:', ''))

    if version >= 1066002:
        index = {}
        num = stream.readInt32()
        for i in range(num):
            key = stream.readString7()
            value = stream.readInt32()
            index[key] = value

        for key, val in index.items():
            stream.base_stream.seek(val)
            tag = stream.readString7()
            if tag in TagReaders:
                retTagData[tag] = TagReaders[tag](stream, version=version)
            else:
                print('#### NO READER AVAILABLE FOR', tag)

        return retTagData
    else:
        LoadOldVersion(stream)
