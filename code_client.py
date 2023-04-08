from secrets import secrets
import wifi
import socketpool
import time
import errno

# 10.26.46.142
HOST = '10.26.46.142'
PORT = 8080
TIMEOUT = None
BUFSIZE = 64
clients = {}
connections = {}
server_socket = None
client_socket = None

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

def init_recv(host, port, timeout):
    global server_socket
    print("TCP Server at ", end="")
    print(wifi.radio.ipv4_address)
    pool = socketpool.SocketPool(wifi.radio)
    server_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.settimeout(timeout)
    server_socket.setblocking(False)
    server_socket.listen(16)

def accept_clients():
    global server_socket
    try:
        conn, addr = server_socket.accept()
        if conn:
            conn.settimeout(TIMEOUT)
            print("Accepted from", addr)
            clients[addr] = {
                'conn': conn,
                'buf': bytearray([0] * BUFSIZE),
                'addr': addr,
                'buf_pointer': 0,
                'poe': time.monotonic
            }
    except:
        pass

def recv_clients():
    for client in clients.values():
        i = client['conn'].recv_into(memoryview(client['buf'])[client['buf_pointer']:], BUFSIZE - client['buf_pointer'])
        client['buf_pointer'] = client['buf_pointer'] + i
        if client['buf_pointer'] == BUFSIZE:
            client['buf_pointer'] = 0
        if i != 0:
            print(client['buf'])
        decoded_buffer = client['buf'].decode()
        if "thump-thump" in decoded_buffer:
            client['buf'] = bytearray([0] * BUFSIZE)
            client['poe'] = time.monotonic
        if time.monotonic() - client['poe'] > 2:
            print("client heartbeat error!")
            exit()

def new_connection(host, port, timeout):
    global client_socket
    if connections[(host, port)]:
        return
    pool = socketpool.SocketPool(wifi.radio)
    client_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    client_socket.setblocking(False)
    client_socket.connect((host, port))
    client_socket.settimeout(timeout)
    connections[(host, port)] = client_socket

def hearbeat():
    for connection in connections.values():
        connection.send(b'hello, my name is han tyumi')
    
connect_wifi()
init_recv('0.0.0.0', PORT, None)
def loop():
    new_connection(HOST, PORT, None)
    accept_clients()
    recv_clients()
    hearbeat()

while True:
    loop()