from math import floor

KEY = "secret"
alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':.,/-_0123456789{}\"[] "

def encrypt(key, clear):
    enc = []
    for i in range(len(clear)):
        enc.append(alphabet[(alphabet.index(clear[i]) + alphabet.index(key[i % len(key)])) % len(alphabet)])
    return "".join(enc)

def decrypt(key, enc):
    dec = []
    for i in range(len(enc)):
        dec.append(alphabet[(len(alphabet) + alphabet.index(enc[i]) - alphabet.index(key[i % len(key)])) % len(alphabet)])
    return "".join(dec)


class Packet():
    def __init__(self, from_addr: int, to_addr: int, encoded_message: str):
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.encoded_message = encoded_message
        self.checksum = 0

        self.compute_checksum()

    def compute_checksum(self):
        nleft = len(self.encoded_message)
        sum = 0
        pos = 0
        while nleft > 1:
            sum = ord(self.encoded_message[pos]) * 256 + \
                (ord(self.encoded_message[pos + 1]) + sum)
            pos = pos + 2
            nleft = nleft - 2
        if nleft == 1:
            sum = sum + ord(self.encoded_message[pos]) * 256

        sum = (sum >> 16) + (sum & 0xFFFF)
        sum += (sum >> 16)
        sum = (~sum & 0xFFFF)

        self.checksum = sum

class RadioProtocol:
    def __init__(self, address: int):
        self.addr = address
        self.group = floor(address / 100) * 100

    def send_packet(self, message, addrDest: int) -> str:
        packet = Packet(self.addr, addrDest, encrypt(KEY, message))
        return "|".join([str(packet.to_addr), str(packet.from_addr), str(packet.encoded_message), str(packet.checksum)])

    def receive_packet(self, string_packet: str):
        if string_packet != None:
            string_packet = string_packet.split("|")
            packet = Packet(int(string_packet[1]), int(string_packet[0]), string_packet[2])
            packet = packet if int(string_packet[3]) == packet.checksum else None
            if packet != None:
                if self.addr == packet.to_addr or self.group == packet.to_addr:
                    packet.encoded_message = decrypt(KEY, packet.encoded_message)
                    return packet
                else:
                    return -1
            else:
                return 2
        return None


def escape_attribute(string):
    return string.replace('"', "").replace("'", "").lstrip()


def parse_single_feature_line(attributestring):
    try:
        attributestring = attributestring.replace("{", "").replace("}", "")
        attributes = dict()
        for keyvaluepair in attributestring.split(','):
            key, value = keyvaluepair.split(':')
            attributes[escape_attribute(key)] = escape_attribute(value)
        return attributes
    except:
        return None
