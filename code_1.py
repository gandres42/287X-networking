from secrets import secrets
import wifi
import socketpool
import time
import errno
# import json

# used only for testing & demonstration
CLIENT_IP = "10.26.40.218"
SERVER_IP = "10.26.42.121"

BUFSIZE = 128

pending = {}
accepting = {}
connections = {}

def connect_wifi():
    connected = False
    while not connected:
        print("Connecting to %s" % secrets["ssid"])
        try:
            wifi.radio.connect(secrets["ssid"], secrets["password"])
            print("Connected to %s!" % secrets["ssid"])
            connected = True
        except ConnectionError as e:
            print("Failed to connect to Wifi, trying again")

def start_accepting(host, port, timeout):
    global accepting
    print("Accepting connections at ", end="")
    print(wifi.radio.ipv4_address)
    pool = socketpool.SocketPool(wifi.radio)
    server_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.settimeout(timeout)
    server_socket.setblocking(False)
    server_socket.listen(16)
    accepting[(host, port)] = server_socket

def stop_accepting(host, port):
    global accepting
    accepting.remove((host, port))

def accept_clients():
    global accepting
    for socket in accepting.values():
        try:
            sock, addr = socket.accept()
            if sock:
                sock.settimeout(None)
                print("Accepted from", addr)
                connections[addr] = {
                    'sock': sock,
                    'buf': bytearray([0] * BUFSIZE),
                    'addr': addr,
                    'buf_pointer': 0,
                    'last_recv': time.monotonic(),
                    'last_send': time.monotonic()
                }
        except:
            pass

# def extract_json_messages(buffer):
#     messages = []
#     while True:
#         try:
#             decoded = buffer.decode()
#             index = decoded.index('{')
#             message = json.loads(decoded[index:])
#             messages.append(message)
#             buffer = buffer[index + len(json.dumps(message).encode('utf-8')):]
#         except (ValueError, UnicodeDecodeError):
#             break
        
#     return messages, buffer

def recv():
    for client in connections.values():
        try:
            i = client['sock'].recv_into(memoryview(client['buf'])[client['buf_pointer']:], BUFSIZE - client['buf_pointer'])
            client['last_recv'] = time.monotonic()
            client['buf_pointer'] = client['buf_pointer'] + i
            if client['buf_pointer'] == BUFSIZE:
                client['buf_pointer'] = 0
            print(client['buf'])
        except:
            pass

def broadcast(msg):
    for client in connections.values():
        client['sock'].send(msg.encode())

def new_connection(host, port, timeout):
    global pending
    if (host, port) in connections.keys() or (host, port) in pending.keys():
        return
    pool = socketpool.SocketPool(wifi.radio)
    new_sock = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    new_sock.settimeout(timeout)
    new_sock.setblocking(False)
    pending[(host, port)] = new_sock
    return (host, port)

def try_connections():
    global pending
    for conn in pending.items():
        try:
            host = conn[0][0]
            port = conn[0][1]
            conn[1].connect((host, port))
            print("Connected to " + host)
            connections[(host, port)] = {
                'sock': conn[1],
                'buf': bytearray([0] * BUFSIZE),
                'addr': host,
                'buf_pointer': 0,
                'last_recv': time.monotonic(),
                'last_send': time.monotonic()
            }
            pending.remove((host, port))
        except:
            pass    
    
def heartbeat():
    for connection in connections.values():
        if time.monotonic() - connection['last_recv'] >= 3:
            connection['sock'].close()
            # print("Connection timed out!")
        elif time.monotonic() - connection['last_send'] >= 1:
            connection['sock'].setblocking(True)
            connection['sock'].send(b'hello')
            connection['last_send'] = time.monotonic()
            connection['sock'].setblocking(False)

def loop():
    accept_clients()
    try_connections()
    recv()
    heartbeat()

connect_wifi()
print(str(wifi.radio.ipv4_address))
if str(wifi.radio.ipv4_address) == SERVER_IP:
    print("I am the server!")
    start_accepting('0.0.0.0', 8080, None)
elif str(wifi.radio.ipv4_address) == CLIENT_IP:
    print("I am the client!")
    new_connection(SERVER_IP, 8080, None)

while True:
    loop()