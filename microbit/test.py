from Collect.protocol import RadioProtocol, parse_single_feature_line
import time
from Collect.protocol import Encryption, Format

key = "a"

truc = Encryption(key)
form = Format


protocol_envoi = RadioProtocol(0, truc, form)

protocol_reception = RadioProtocol(1, truc, form)

#[{"latitude":45.723967,"intensity":30,"radius":10,"id":"9560c125-ad99-4b54-a08d-19079a7f1ddb","longitude":4.907738,"updatedAt":"2021-12-15T10:15:48.167Z","createdAt":"2021-12-15T10:15:48.167Z"}][END]


if __name__ == "__main__":

    envoie = {"latitude":45.723967,"intensity":30,"radius":10,"id":"9560c125-ad99-4b54-a08d-19079a7f1ddb","longitude":4.907738}
    
    paquet = protocol_envoi.send_packet(str(envoie), 1)

    #print("log env:", envoie)
    #print("packet env:", paquet)
    
    truc = protocol_reception.receive_packet(str(paquet))
    recu = parse_single_feature_line(truc)

    #print("packet rec:", truc)
    print("packet traiter", recu)



