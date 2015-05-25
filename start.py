import getpass
import sys
from optparse import OptionParser

from minecraft import authentication
from minecraft.exceptions import YggdrasilError
from minecraft.networking.connection import Connection
from minecraft.networking.packets import *
from minecraft.compat import input
import time


def get_options():
    parser = OptionParser()

    parser.add_option("-u", "--username", dest="username", default=None,
                      help="username to log in with")

    parser.add_option("-p", "--password", dest="password", default=None,
                      help="password to log in with")

    parser.add_option("-s", "--server", dest="server", default=None,
                      help="server to connect to")

    (options, args) = parser.parse_args()
    
    options.username = "simon@catbus.co.uk"
    options.password = "VTKgPqnbeYGrivXdxNcXJcD"
    options.server = "dustbunny.catbus.co.uk:25565"
    if not options.username:
        options.username = input("Enter your username: ")

    if not options.password:
        options.password = getpass.getpass("Enter your password: ")

    if not options.server:
        options.server = input("Please enter server address"
                               " (including port): ")
    # Try to split out port and address
    if ':' in options.server:
        server = options.server.split(":")
        options.address = server[0]
        options.port = int(server[1])
    else:
        options.address = options.server
        options.port = 25565

    return options

class Speaker():
    def __init__(self, main):
        self.main = main
    def write(self, value):
        self.main.speak(value)
        sys.__stdout__.write(value)


class Main(object):
    def __init__(self, options):
        self.auth_token = authentication.AuthenticationToken()
        try:
            self.auth_token.authenticate(options.username, options.password)
        except YggdrasilError as e:
            print(e)
            sys.exit()
        print("Logged in as " + self.auth_token.username)
        self.network = Connection(options.address, options.port, self.auth_token)
        self.network.connect()
        self.register_listeners()
        #sys.stdout = Speaker(self)
        while not self.network.playing: pass
        self.respawn()
        while True:
            try: self.tick()
            except KeyboardInterrupt:
                print("Bye!")
                sys.exit()

    def register_listeners(self):
        self.network.register_packet_listener(self.print_chat, ChatMessagePacket)
        self.network.register_packet_listener(self.set_pos, PlayerPositionAndLookPacket)
        self.network.register_packet_listener(self.recieve_plugin_message, PluginMessage)
        self.network.register_packet_listener(self.set_health, UpdateHealth)

    def tick(self):
        text = input()
        self.speak(text)
        
    def speak(self, message):
        packet = ChatPacket()
        packet.message = message
        self.network.write_packet(packet)
    
    def set_health(self, health_packet):
        if health_packet.health == 0.0:
            print "RESPAWN"
            self.respawn()
            
    def respawn(self):
        packet = ClientStatus()
        packet.action_id = 0
        self.network.write_packet(packet)
        #print packet
            
    def print_chat(self, chat_packet):
        print type(chat_packet)
        print("Position: " + str(chat_packet.position))
        print("Data: " + chat_packet.json_data)

    def recieve_plugin_message(self, plugin_message):
        data = plugin_message.data.split("|")
        if len(data) == 2 and data[0] == "MC":
            if data[1] == "Brand": print "Brand:", plugin_message.channel
            else:
                print "PLUGIN MESSAGE:", data[1], plugin_message.channel
    
    def set_pos(self, pos_packet):
        print "SET POS", pos_packet.x, pos_packet.y, pos_packet.z


def main():
    options = get_options()
    Main(options)

if __name__ == "__main__":
    main()
