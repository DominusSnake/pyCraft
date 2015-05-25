import json
from collections import OrderedDict

types = ['Slot', 'VarInt', 'Short', 'End', 'VarIntPrefixedByteArray', 'ShortPrefixedByteArray', 'Double', 'List', 'Long', 'UnsignedShort', 'IntArray', 'Position', 'Nbt', 'Type', 'String', 'UnsignedByte', 'Float', 'Boolean', 'Integer', 'Byte', 'UnsignedLong']
for t in types:
    globals()[t] = t

class Packet(object):
    def __init__(self): pass

class HandShakePacket(Packet):
    id = 0x00
    packet_name = "handshake"
    definition = [
        {'protocol_version': VarInt},
        {'server_address': String},
        {'server_port': UnsignedShort},
        {'next_state': VarInt}]

STATE_HANDSHAKE_CLIENTBOUND = {

}
STATE_HANDSHAKE_SERVERBOUND = {
    0x00: HandShakePacket
}

# Status State
# ==============
class ResponsePacket(Packet):
    id = 0x00
    packet_name = "response"
    definition = [
        {'json_response': String}]

class PingPacketResponse(Packet):
    id = 0x01
    packet_name = "ping"
    definition = [
        {'time': Long}]

STATE_STATUS_CLIENTBOUND = {
    0x00: ResponsePacket,
    0x01: PingPacketResponse
}

class RequestPacket(Packet):
    id = 0x00
    packet_name = "request"
    definition = []

class PingPacket(Packet):
    id = 0x01
    packet_name = "ping"
    definition = [
        {'time': Long}]

STATE_STATUS_SERVERBOUND = {
    0x00: RequestPacket,
    0x01: PingPacket
}

# Login State
# ==============
class DisconnectPacket(Packet):
    id = 0x00
    packet_name = "disconnect"
    definition = [
        {'json_data': String}]

class EncryptionRequestPacket(Packet):
    id = 0x01
    packet_name = "encryption request"
    definition = [
        {'server_id': String},
        {'public_key': VarIntPrefixedByteArray},
        {'verify_token': VarIntPrefixedByteArray}]

class LoginSuccessPacket(Packet):
    id = 0x02
    packet_name = "login success"
    definition = [
        {'UUID': String},
        {'Username': String}]

class SetCompressionPacket(Packet):
    id = 0x03
    packet_name = "set compression"
    definition = [
        {'threshold': VarInt}]

STATE_LOGIN_CLIENTBOUND = {
    0x00: DisconnectPacket,
    0x01: EncryptionRequestPacket,
    0x02: LoginSuccessPacket,
    0x03: SetCompressionPacket
}

class LoginStartPacket(Packet):
    id = 0x00
    packet_name = "login start"
    definition = [
        {'name': String}]

class EncryptionResponsePacket(Packet):
    id = 0x01
    packet_name = "encryption response"
    definition = [
        {'shared_secret': VarIntPrefixedByteArray},
        {'verify_token': VarIntPrefixedByteArray}]

STATE_LOGIN_SERVERBOUND = {
    0x00: LoginStartPacket,
    0x01: EncryptionResponsePacket
}

# Playing State
# ==============

class KeepAlivePacket(Packet):
    id = 0x00
    packet_name = "keep alive"
    definition = [
        {'keep_alive_id': VarInt}]

class JoinGamePacket(Packet):
    id = 0x01
    packet_name = "join game"
    definition = [
        {'entity_id': Integer},
        {'game_mode': UnsignedByte},
        {'dimension': Byte},
        {'difficulty': UnsignedByte},
        {'max_players': UnsignedByte},
        {'level_type': String},
        {'reduced_debug_info': Boolean}]

class ChatMessagePacket(Packet):
    id = 0x02
    packet_name = "chat message"
    definition = [
        {'json_data': String},
        {'position': Byte}]

class TimeUpdate(Packet):
    id = 0x03
    packet_name = "tick"
    definition = [
        {"world_age": Long},
        {"day_time": Long}
    ]

class EntityEquipment(Packet):
    id = 0x04
    packet_name = "set entity equipment"
    definition = [
        {"entity_id": VarInt},
        {"slot": Short},
        {"item": Slot}
    ]

class SetSpawn(Packet):
    id = 0x05
    packet_name = "set spawn"
    definition = [
        {'pos': Position}
    ]
    
class UpdateHealth(Packet):
    id = 0x06
    packet_name = "update health"
    definition = [
        {"health": Float},
        {"food": VarInt},
        {"saturation": Float}
    ]
    
class Respawn(Packet):
    id = 0x07
    packet_name = "respawn"
    definition = [
        {"dimension": Integer},
        {"difficulty": UnsignedByte},
        {"gamemode": UnsignedByte},
        {"level_type": String}
    ]
    
class PlayerPositionAndLookPacket(Packet):
    id = 0x08
    packet_name = "player position and look"
    definition = [
        {'x': Double},
        {'y': Double},
        {'z': Double},
        {'yaw': Float},
        {'pitch': Float},
        {'flags': Byte}]

class UpdateEntity(Packet):
    id = 0x1A
    packet_name = "update entity"
    definition = [
        {'entity_id': Integer},
        {'entity_status': Byte}
    ]

class PluginMessage(Packet):
    id = 0x3f
    packet_name = "plugin message"
    definition = [
        {'channel': String,
         'data': VarIntPrefixedByteArray}
    ]

class DisconnectPacketPlayState(Packet):
    id = 0x40
    packet_name = "disconnect"

    definition = [
        {'json_data': String}]

class ServerDifficulty(Packet):
    id = 0x41
    packet_name = "server difficulty"
    definition = [{
        "difficulty": UnsignedByte
    }]

class SetCompressionPacketPlayState(Packet):
    id = 0x46
    packet_name = "set compression"
    definition = [
        {'threshold': VarInt}]

STATE_PLAYING_CLIENTBOUND = {
    0x00: KeepAlivePacket,
    0x01: JoinGamePacket,
    0x02: ChatMessagePacket,
    0x03: TimeUpdate,
    0x04: EntityEquipment,
    0x05: SetSpawn,
    0x06: UpdateHealth,
    0x07: Respawn,
    0x08: PlayerPositionAndLookPacket,
#    0x09: HeldItemChange,
#    0x0A: UseBed,
#    0x0B: SetAnimation,
#    0x0C: SpawnPlayer,
#    0x0D: CollectItem,
#    0x0E: SpawnObject,
#    0x0F: SpawnMob,
    0x1A: UpdateEntity,
    0x3f: PluginMessage, 
    0x40: DisconnectPacketPlayState,
    0x41: ServerDifficulty,
    0x46: SetCompressionPacketPlayState
}

class ChatPacket(Packet):
    id = 0x01
    packet_name = "chat"
    definition = [
        {'message': String}]

class PositionAndLookPacket(Packet):
    id = 0x06
    packet_name = "position and look"
    definition = [
        {'x': Double},
        {'feet_y': Double},
        {'z': Double},
        {'yaw': Float},
        {'pitch': Float},
        {'on_ground': Boolean}]

class ClientStatus(Packet):
    id = 0x16
    packet_name =  "client status"
    definition = [
        {"action_id": VarInt}
    ]

STATE_PLAYING_SERVERBOUND = {
    0x00: KeepAlivePacket,
    0x01: ChatPacket,
    0x06: PositionAndLookPacket,
    0x16: ClientStatus
}

states = {
    "handshake": {},
    "status": {},
    "login": {},
    "playing": {}}

for state in states:
    bounds = ["CLIENTBOUND", "SERVERBOUND"]
    for bound in bounds:
        states[state][bound] = OrderedDict()
        packets = globals()["STATE_"+state.upper()+"_"+bound]
        for key in sorted(packets.keys()):
            packet = packets[key]
            assert(key == packet.id)
            sorted_dict = OrderedDict((\
                ("id", key), \
                ("friendly_name", packet.packet_name), \
                ("definition", packet.definition)))
            states[state][bound][packet.__name__] = sorted_dict


json_file = open("packets.json", "w")
json.dump(states, json_file, indent=2)
json_file.close()