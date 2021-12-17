from math import floor


class Encryption():
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':.,/-_0123456789{}()\" "

    def __init__(self, key):
        self.key = key

    @staticmethod
    def chr(index: int) -> str:
        try:
            return Encryption.alphabet[index]
        except IndexError:
            raise Exception("Encyption does not support <>")

    @staticmethod
    def ord(char: str) -> int:
        try:
            return Encryption.alphabet.index(char)
        except ValueError:
            raise Exception("Encyption does not support <>")

    def encrypt(self, clear):
        enc = []
        for i in range(len(clear)):
            key_c = self.key[i % len(self.key)]
            enc_c = Encryption.chr(
                (Encryption.ord(clear[i]) + Encryption.ord(key_c)) % len(Encryption.alphabet))
            enc.append(enc_c)
        return "".join(enc)

    def decrypt(self, enc):
        dec = []
        for i in range(len(enc)):
            key_c = self.key[i % len(self.key)]
            dec_c = Encryption.chr((len(Encryption.alphabet) + Encryption.ord(
                enc[i]) - Encryption.ord(key_c)) % len(Encryption.alphabet))
            dec.append(dec_c)
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


class Format():
    def dumps(self, packet: Packet) -> str:
        return "|".join([str(packet.to_addr), str(packet.from_addr), str(packet.encoded_message), str(packet.checksum)])

    def parse(self, string: str) -> Packet:
        packet = string.split("|")
        return Format.compare_checksum(self, Packet(int(packet[1]), int(packet[0]), packet[2]), packet[3])

    def compare_checksum(self, compute_packet: Packet, received_checksum: str) -> Packet:
        return compute_packet if int(received_checksum) == compute_packet.checksum else None


class RadioProtocol:
    def __init__(self, address: int, encryption: Encryption, format: Format):
        self.addr = address
        self.encryption = encryption
        self.format = format
        self.group = math.floor(address / 100) * 100

    def send_packet(self, message, addrDest: int) -> str:
        packet = Packet(self.addr, addrDest, self.encryption.encrypt(message))
        return self.format.dumps(self, packet)

    def receive_packet(self, string_packet: str):
        if string_packet != None:
            packet = self.format.parse(self, string_packet)
            if packet != None:
                if self.addr == packet.to_addr or self.group == packet.to_addr:
                    packet.encoded_message = self.encryption.decrypt(
                        packet.encoded_message)
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
