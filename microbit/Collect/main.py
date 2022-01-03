from microbit import uart, display
import radio
from gc import collect
from protocol import RadioProtocol, parse_single_feature_line
from machine import reset
from sys import exit

radio.config(group=199, address=0x24667818, length=251)
radio.on()

protocol = RadioProtocol(0)
serial_uart = uart.init(baudrate=115200)

def send_to_gateway(content):
    uart.write(str(content) + PACKET_END)

PACKET_END = "[END]"
LAST_MESSAGE = ""
ADDRESS_DEST = 0

data = {}
try:
    while True:
        new_log_packet = radio.receive()
        if new_log_packet != None:
            packet_obj = protocol.receive_packet(str(new_log_packet))
            request = parse_single_feature_line(packet_obj.encoded_message)
            if not request:
                continue
            if request == 2:
                data["ack"] = 1
                send_to_gateway(data)
            elif request == -1:
                pass
            else:
                if "ack" in request and request["ack"] == 0:
                    data["ack"] = 0
                    send_to_gateway(data)
                elif "ack" in request and request["ack"] != 0:
                    data["ack"] = request["ack"]
                    send_to_gateway(data)
                else:
                    data["ack"] = 0
                    radio.send(protocol.send_packet(str(data), packet_obj.from_addr))
                    send_to_gateway(packet_obj.encoded_message)

        serial = uart.read()
        if serial != None:
            if "MicroPython" in serial or 'Type "help()"' in serial:
                continue
            LAST_MESSAGE += str(serial).replace("b'", "").replace("'", "").replace(PACKET_END, "")
            if "cmd" in LAST_MESSAGE:
                cmd = parse_single_feature_line(LAST_MESSAGE)
                if cmd and cmd["cmd"] == "reset":
                    print("reset" + PACKET_END)
                    LAST_MESSAGE = ""
                    exit()
            else:
                radio.send(protocol.send_packet(LAST_MESSAGE, ADDRESS_DEST))
                LAST_MESSAGE = ""

        collect()
except Exception as err:
    send_to_gateway(str(err))
    reset()
