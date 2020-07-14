import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)
import socket
import struct
import threading
import json
import time
import ssl

PORT = 1234
HEADER_LENGTH = 2


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
    sock.sendall(message);


# funkcija za komunikacijo z odjemalcem (tece v loceni niti za vsakega odjemalca)
def client_thread(client_sock, client_addr):
    global clients
    global users
    ime = None

    print("[system] connected with " + client_addr[0] + ":" + str(client_addr[1]))
    print("[system] we now have " + str(len(clients)) + " clients")
    print("")

    try:

        while True:  # neskoncna zanka
            msg_received = receive_message(client_sock)

            if not msg_received:  # ce obstaja sporocilo
                break


            #ime uporabnika dobimo iz certifikata
            cert = client_sock.getpeercert()
            for sub in cert['subject']:
                for key, value in sub:
                    # v commonName je ime uporabnika
                    if key == 'commonName':
                      source = value.upper()
            if ime is None:
                ime = source
                users[ime] = client_sock
            message_format = json.loads(msg_received)
            _, destination, message, time = message_format.values()
            if destination == "":
                print(time + " <" + source + "> " + message)
                message_format["source"] = source
                json_message = json.dumps(message_format)
                for client in clients:
                    send_message(client, json_message)

    except:
        # tule bi lahko bolj elegantno reagirali, npr. na posamezne izjeme. Trenutno kar pozremo izjemo
        pass

    # prisli smo iz neskoncne zanke
    with clients_lock:
        clients.remove(client_sock)
    print("[system] we now have " + str(len(clients)) + " clients")
    client_sock.close()


def setup_SSL_context():
    # uporabi samo TLS, ne SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    # certifikat je obvezen
    context.verify_mode = ssl.CERT_REQUIRED
    # nalozi svoje certifikate
    context.load_cert_chain(certfile="server.pem", keyfile="serverkey.pem")
    # nalozi certifikate CAjev, ki jim zaupas
    # (samopodp. cert. = svoja CA!)
    context.load_verify_locations('clients.pem')
    # nastavi SSL CipherSuites (nacin kriptiranja)
    context.set_ciphers('AES128-SHA')
    return context


# kreiraj socket
my_ssl_ctx = setup_SSL_context()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", PORT))
server_socket.listen(1)

# cakaj na nove odjemalce
print("[system] listening ...")
clients = set()
clients_lock = threading.Lock()

# online users
users = dict()

while True:
    try:
        client_sock, client_addr = server_socket.accept()
        client_sock = my_ssl_ctx.wrap_socket(client_sock, server_side=True)

        #ime uporabnika dobimo iz certifikata
        cert = client_sock.getpeercert()
        for sub in cert['subject']:
          for key, value in sub:
            # v commonName je ime uporabnika
            if key == 'commonName':
              user = value
        print('Established SSL connection with: ', user.upper())
        # pocakaj na novo povezavo - blokirajoc klic
        with clients_lock:
            clients.add(client_sock)

        thread = threading.Thread(target=client_thread, args=(client_sock, client_addr));
        thread.daemon = True
        thread.start()

    except KeyboardInterrupt:
        break

print("[system] closing server socket ...")
server_socket.close()
