from secrets import secrets
import wifi
import socketpool
import time
import json

# used only for testing & demonstration
CLIENT_IP = "10.26.40.217"
SERVER_IP = "10.26.40.218"
BUFSIZE = 64
NODE_TYPE = 0

pool = socketpool.SocketPool(wifi.radio)
socket = None
clients = {}
client_buf = bytearray([0] * BUFSIZE)
client_buf_pointer = 0

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
    global socket, pool
    print("Accepting connections at ", end="")
    print(wifi.radio.ipv4_address)
    socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    socket.bind((host, port))
    socket.settimeout(timeout)
    socket.setblocking(False)
    socket.listen(255)

def accept_clients():
    global socket, pool
    try:
        sock, addr = socket.accept()
        if sock:
            print("Accepted from", addr)
            sock.settimeout(None)
            sock.setblocking(False)
            clients[addr] = {
                'sock': sock,
                'buf': bytearray([0] * BUFSIZE),
                'addr': addr,
                'buf_pointer': 0
            }
    except Exception as e:
        pass

def extract_json_messages(buffer):
    messages = []
    while True:
        try:
            decoded = buffer.decode()
            index = decoded.index('{')
            message = json.loads(decoded[index:])
            messages.append(message)
            buffer = buffer[index + len(json.dumps(message).encode()):]
        except:
            break
    return messages, buffer

def buffer_tostring(buffer, pointer):
    str_buf = buffer.decode()
    print(str_buf)
    str_buf = str_buf[pointer:] + str_buf[0:pointer]
    return str_buf

def server_recv():
    for client in clients.values():
        try:
            i = client['sock'].recv_into(memoryview(client['buf'])[client['buf_pointer']:], BUFSIZE - client['buf_pointer'])
            if i == 0:
                client['sock'].close()
                clients.pop(client['addr'])
            else:
                client['last_recv'] = time.monotonic()
                client['buf_pointer'] = client['buf_pointer'] + i
                if client['buf_pointer'] == BUFSIZE:
                    client['buf_pointer'] = 0
                print(client['buf'])
                try:
                    messages, tmp = extract_json_messages(client['buf'])
                except Exception as e:
                    print(e)
                print(messages)
        except Exception as e:
            pass

def client_recv():
    global socket, pool
    try:
        i = socket.recv_into(memoryview(client_buf)[client_buf_pointer:], BUFSIZE - client_buf_pointer)
        if i == 0:
            socket.close()
            socket = None
        else:
            if client_buf_pointer == BUFSIZE:
                client_buf_pointer = 0
    except Exception as e:
        pass

def broadcast(msg):
    for client in clients.values():
        client['sock'].send(msg.encode())

def new_connection(host, port, timeout):
    global socket, pool
    socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    socket.settimeout(timeout)
    socket.setblocking(False)
    try:
        socket.connect((host, port))
    except:
        print("Connection failed") 

def loop():
    global socket, pool
    if NODE_TYPE == 1:
        if socket == None:
            start_accepting('0.0.0.0', 8080, None)
        accept_clients()
        server_recv()
    if NODE_TYPE == 2:
        if socket == None:
            new_connection(SERVER_IP, 8080, None)
        else:
            client_recv()


connect_wifi()
print(str(wifi.radio.ipv4_address))
if str(wifi.radio.ipv4_address) == SERVER_IP:
    print("I am the server!")
    NODE_TYPE = 1
elif str(wifi.radio.ipv4_address) == CLIENT_IP:
    print("I am the client!")
    NODE_TYPE = 2

while True:
    loop()