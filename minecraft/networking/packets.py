from io import BytesIO
import json, os, warnings
from zlib import compress

import minecraft.networking.types as types

class PacketBuffer(object):
    def __init__(self):
        self.bytes = BytesIO()

    def send(self, value):
        """
        Writes the given bytes to the buffer, designed to emulate socket.send
        :param value: The bytes to write
        """
        self.bytes.write(value)

    def read(self, length):
        return self.bytes.read(length)

    def recv(self, length):
        return self.read(length)

    def reset(self):
        self.bytes = BytesIO()

    def reset_cursor(self):
        self.bytes.seek(0)

    def get_writable(self):
        return self.bytes.getvalue()

class PacketListener(object):
    def __init__(self, callback, *args):
        self.packets_to_listen = []
        self.callback = callback
        for arg in args:
            if issubclass(arg, Packet):
                self.packets_to_listen.append(arg)

    def call_packet(self, packet):
        for packet_type in self.packets_to_listen:
            if isinstance(packet, packet_type):
                self.callback(packet)

class Packet(object):
    packet_name = "base"
    id = -0x01
    definition = []

    def __init__(self, **kwargs):
        pass

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def get_data_type(self, datatype):
        try:
            if isinstance(datatype, list):
                if getattr(self, datatype[1]) in datatype[2:]:
                    return types.__dict__[datatype[0]]
                else:
                    return types.Type
            return types.__dict__[datatype]
        except KeyError:
            warnings.warn("Datatype %s not found"%datatype)
            return types.Type

    def read(self, file_object):
        for field in self.definition:
            for var_name, data_type in field.items():
                if hasattr(self, var_name) and isinstance(getattr(self, varname), types.Type): continue
                data_type = self.get_data_type(data_type)
                value = data_type.read(file_object)
                setattr(self, var_name, value)

    def write(self, socket, compression_threshold=None):
        # buffer the data since we need to know the length of each packet's
        # payload
        packet_buffer = PacketBuffer()
        # write packet's id right off the bat in the header
        types.VarInt.send(self.id, packet_buffer)

        for field in self.definition:
            for var_name, data_type in field.items():
                data_type = self.get_data_type(data_type)
                data = getattr(self, var_name)
                data_type.send(data, packet_buffer)

        # compression_threshold of None means compression is disabled
        if compression_threshold is not None:
            if len(packet_buffer.get_writable()) > compression_threshold != -1:
                # compress the current payload
                compressed_data = compress(packet_buffer.get_writable())
                packet_buffer.reset()
                # write out the length of the compressed payload
                types.VarInt.send(len(compressed_data), packet_buffer)
                # write the compressed payload itself
                packet_buffer.send(compressed_data)
            else:
                # write out a 0 to indicate uncompressed data
                packet_data = packet_buffer.get_writable()
                packet_buffer.reset()
                types.VarInt.send(0, packet_buffer)
                packet_buffer.send(packet_data)

        types.VarInt.send(len(packet_buffer.get_writable()), socket)  # Packet Size
        socket.send(packet_buffer.get_writable())  # Packet Payload

json_file = open(os.path.dirname(os.path.abspath(__file__))+"/packets.json")
packets = json.load(json_file)
json_file.close()
for state in packets:
    for bound in packets[state]:
        current_state_name = "STATE_"+state.upper()+"_"+bound
        globals()[current_state_name] = {}
        for packet_id in packets[state][bound]:
            packet_class = type(str(packet_id), (Packet,), packets[state][bound][packet_id])
            globals()[str(packet_id)] = packet_class
            globals()[current_state_name][packet_class.id] = packet_class
