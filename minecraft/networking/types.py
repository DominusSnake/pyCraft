"""Contains definitions for minecraft's different data types
Each type has a method which is used to read and write it.
These definitions and methods are used by the packet definitions
"""
import struct, json

class Type(object):
    @staticmethod
    def read(file_object):
        pass
    
    @staticmethod
    def send(value, socket):
        pass

# =========================================================

class End(Type): pass

class Boolean(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('?', file_object.read(1))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('?', value))

class UnsignedByte(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>B', file_object.read(1))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>B', value))

class Byte(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>b', file_object.read(1))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>b', value))

class Short(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>h', file_object.read(2))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>h', value))

class UnsignedShort(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>H', file_object.read(2))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>H', value))

class Integer(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>i', file_object.read(4))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>i', value))

class VarInt(Type):
    @staticmethod
    def read_socket(socket):
        number = 0
        for i in range(5):
            byte = socket.recv(1)
            if byte == "" or len(byte) == 0:
                raise RuntimeError("Socket disconnected")
            byte = ord(byte)
            number |= (byte & 0x7F) << 7 * i
            if not byte & 0x80:
                break
        return number

    @staticmethod
    def read(file_object):
        number = 0
        for i in range(5):
            byte = ord(file_object.read(1))
            number |= (byte & 0x7F) << 7 * i
            if not byte & 0x80:
                break
        return number

    @staticmethod
    def send(value, socket):
        out = bytes()
        while True:
            byte = value & 0x7F
            value >>= 7
            out += struct.pack("B", byte | (0x80 if value > 0 else 0))
            if value == 0:
                break
        socket.send(out)

    @staticmethod
    def size(value):
        for max_value, size in VARINT_SIZE_TABLE.items():
            if value < max_value:
                return size

# Maps (maximum integer value -> size of VarInt in bytes)
VARINT_SIZE_TABLE = {
    2 ** 7: 1,
    2 ** 14: 2,
    2 ** 21: 3,
    2 ** 28: 4,
    2 ** 35: 5,
    2 ** 42: 6,
    2 ** 49: 7,
    2 ** 56: 8,
    2 ** 63: 9,
    2 ** 70: 10,
    2 ** 77: 11,
    2 ** 84: 12
}

class Long(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>q', file_object.read(8))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>q', value))

class UnsignedLong(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>Q', file_object.read(8))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>Q', value))

class Float(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>f', file_object.read(4))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>f', value))

class Double(Type):
    @staticmethod
    def read(file_object):
        return struct.unpack('>d', file_object.read(8))[0]

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('>d', value))

class ShortPrefixedByteArray(Type):
    @staticmethod
    def read(file_object):
        length = Short.read(file_object)
        return struct.unpack(str(length) + "s", file_object.read(length))[0]

    @staticmethod
    def send(value, socket):
        Short.send(len(value), socket)
        socket.send(value)

class VarIntPrefixedByteArray(Type):
    @staticmethod
    def read(file_object):
        length = VarInt.read(file_object)
        return struct.unpack(str(length) + "s", file_object.read(length))[0]

    @staticmethod
    def send(value, socket):
        VarInt.send(len(value), socket)
        socket.send(struct.pack(str(len(value)) + "s", value))

class String(Type):
    @staticmethod
    def read(file_object):
        length = VarInt.read(file_object)
        return file_object.read(length).decode("utf-8")

    @staticmethod
    def send(value, socket):
        value = value.encode('utf-8')
        VarInt.send(len(value), socket)
        socket.send(value)

class List(Type):
    @staticmethod
    def read(file_object):
        type_id = Byte.read(file_object)
        length = VarInt.read(file_object)
        out = []
        for i in range(length):
            out.append(tags[type_id].read(file_object))
        return [type_id, out]
    
    @staticmethod
    def send(value, socket):
        type_id = value[0]
        Byte.send(type_id)
        VarInt.send(len(value[1]))
        for i in value[1]:
            tags[type_id].send(i, socket)
            
class IntArray(Type):
    @staticmethod
    def read(file_object):
        length = VarInt.read(file_object)
        out = []
        for i in range(length):
            out.append(Integer.read(file_object))
        return out
    
    @staticmethod
    def send(value, socket):
        VarInt.send(len(value))
        for i in value:
            Integer.send(i, socket)

class Position(Type):
    @staticmethod
    def read(file_object):
        val = UnsignedLong.read(file_object)
        x = val >> 38
        y = (val >> 26) & 0xFFF
        z = val & 0x3FFFFFF
        if x >= 2**25: x -= 2**26 
        if y >= 2**11: y -= 2**12
        if z >= 2**25: z -= 2**26 
        return x,y,z
        
    @staticmethod
    def send(value, socket):
        Long.send(((x & 0x3FFFFFF) << 38) | ((y & 0xFFF) << 26) | (z & 0x3FFFFFF), socket)

class Chat(Type):
    @staticmethod
    def read(file_object):
        return json.loads(String.read(file_object))
    
    @staticmethod
    def send(value, socket):
        String.send(json.dumps(value), socket)

class Nbt(Type):
    @staticmethod
    def read(file_object):
        print ord(file_object.read(1))
    
    @staticmethod
    def send(file_object):
        pass
    
tags = [
    End,
    Byte,
    Short,
    Integer,
    Long,
    Float,
    Double,
    VarIntPrefixedByteArray,
    String,
    List,
    Nbt,
    IntArray]

class Slot(Type):
    @staticmethod
    def read(file_object):
        item = {}
        item["id"] = Short.read(file_object)
        if item["id"] == -1:
            return item
        item["count"] = Byte.read(file_object)
        item["damage"] = Short.read(file_object)
        has_nbt = Byte.read(file_object)
        #if has_nbt:
            #file_object.seek(file_object.tell()-1)
            #item["nbt"] = Nbt.read(file_object)
        return item

    @staticmethod
    def send(value, socket):
        socket.send(struct.pack('?', value))
