from microbit import *
from protocol import RadioProtocol, parse_single_feature_line
import radio

radio.config(group=199, address=0x24667818, length=251)
radio.on()

protocol = RadioProtocol(0)

serial_uart = uart.init(baudrate=115200)

def send_to_gateway(content):
    uart.write(content)

def send_to_sensors(packet):
    radio.send(packet)

PACKET_END = "[END]"

LAST_PACKET = b""

data = {}

while True:
    new_log_packet = radio.receive()
    if new_log_packet != None:
        packet_obj = protocol.receive_packet(str(new_log_packet))
        request = parse_single_feature_line(packet_obj.encoded_message)
        #ACK
        if request == 2:
            #renvoyer acquittement gateway node Nok 
            data["ack"] = 1
            send_to_gateway(data)
        elif request == -1:
            pass
        else:
            if "ack" in request and request["ack"] == 0:
                #envoie ack ok gateway
                data["ack"] = 0
                send_to_gateway(data)
            elif "ack" in request and request["ack"] != 0:
                #envoie erreur ack gateway
                data["ack"] = request["ack"]
                send_to_gateway(data)
            else: 
                #renvoie un ack au microbit qui a envoyé  le message
                data["ack"] = 0
                radio.send(protocol.send_packet(str(data), packet_obj.from_addr))

                #todo 
                # traitement message
                send_to_gateway(packet_obj.encoded_message)
            

                
        #UART
        

    # redirect packets from the controller to all sensors
    request = uart.readline()
    if request != None:
        LAST_PACKET += request
        if PACKET_END in LAST_PACKET:
            packet = str(LAST_PACKET).replace("b'", "")[:-1].replace(PACKET_END, "")
            send_to_sensors(packet)
            print(packet)
            #request_content = protocol.receive_packet(packet)
            #print("packet redistributed: ", packet)
            LAST_PACKET = b""
            
            # Send temperature to server through gateway
            # packet = protocol.send_packet(str(data), 1)
            # send_to_gateway(packet + "[END]")
