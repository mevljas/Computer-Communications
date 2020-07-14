import socket
import struct
import sys
import threading
import json
import time

PORT = 1234
HEADER_LENGTH = 2
ime = ""


def receive_fixed_length_msg(sock, msglen):
    message = b''
    while len(message) < msglen:
        chunk = sock.recv(msglen - len(message))  # preberi nekaj bajtov
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        message = message + chunk  # pripni prebrane bajte sporocilu

    return message


def receive_message(sock):
    header = receive_fixed_length_msg(sock,
                                      HEADER_LENGTH)  # preberi glavo sporocila (v prvih 2 bytih je dolzina sporocila)
    message_length = struct.unpack("!H", header)[0]  # pretvori dolzino sporocila v int

    message = None
    if message_length > 0:  # ce je vse OK
        message = receive_fixed_length_msg(sock, message_length)  # preberi sporocilo
        message = message.decode("utf-8")

    return message


def send_message(sock, message):
    encoded_message = message.encode("utf-8")  # pretvori sporocilo v niz bajtov, uporabi UTF-8 kodno tabelo

    # ustvari glavo v prvih 2 bytih je dolzina sporocila (HEADER_LENGTH)
    # metoda pack "!H" : !=network byte order, H=unsigned short
    header = struct.pack("!H", len(encoded_message))

    message = header + encoded_message  # najprj posljemo dolzino sporocilo, slee nato sporocilo samo
    sock.sendall(message)


# message_receiver funkcija tece v loceni niti
def message_receiver():
    global ime
    while True:
        if ime != "":
            msg_received = receive_message(sock)
            if len(msg_received) > 0:  # ce obstaja sporocilo
                if msg_received == "<system> ERROR: User not found!":
                    print(msg_received)
                else:
                    try:
                        message = json.loads(msg_received)
                        source, destination, message, time = message.values()
                        if source.upper() != ime.upper():
                            print(time + " <" + source + "> " + message)  #izpis
                    except:
                        pass



# povezi se na streznik
print("[system] connecting to chat server ...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", PORT))
print("[system] connected!")

# zazeni message_receiver funkcijo v loceni niti
thread = threading.Thread(target=message_receiver)
thread.daemon = True
thread.start()


#prijava
while ime == "":
    ime = input("Vpiši ime: ")

print("[system] logging to chat server ...")
send_message(sock, ime)
print("[system] login successful!")
print("")
print("private message format: /msg|username|message")
print("All other formats are considered as public messages")

# pocakaj da uporabnik nekaj natipka in poslji na streznik
print()
while True:
    try:
        destination = ""
        user_input = input("")
        if "/msg" in user_input:
            comamnd, destination, user_input = user_input.split("|")
        message_format = {
            "source": ime,
            "destination": destination.strip(),
            "message": user_input,
            "time": time.strftime("%H:%M:%S")
        }
        json_message = json.dumps(message_format)

        send_message(sock, json_message)
    except:
        print("<system> ERROR: Wrong input!")
