# from secrets import secrets
# import wifi
# import socketpool
# import time
# import errno
# # 10.26.44.107

# TIMEOUT = None
# HOST = '10.26.46.142'
# PORT = 8080

# connected = False
# while not connected:
#     print("Connecting to %s" % secrets["ssid"])
#     try:
#         wifi.radio.connect(secrets["ssid"], secrets["password"])
#         print("Connected to %s!" % secrets["ssid"])
#         connected = True
#     except ConnectionError as e:
#         print("Failed to connect to Wifi, trying again")

# print(wifi.radio.ipv4_address)
# pool = socketpool.SocketPool(wifi.radio)
# s = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
# s.setblocking(False)
# s.connect((HOST, PORT))
# s.settimeout(TIMEOUT)

# print("Creating Socket")
# while True:
#     print("Sending")
#     try:
#         sent = s.send(b"Hello, world")
#         time.sleep(2)
#     except errno.ENOTCONN as e:
#         print(e)

from secrets import secrets
import wifi
import socketpool
import time
import errno

# 10.26.46.142

TIMEOUT = None
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
    server_socket.bind(('0.0.0.0', PORT))
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
                'buf_pointer': 0
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

def new_connection(host, port, timeout):
    global client_socket
    pool = socketpool.SocketPool(wifi.radio)
    client_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    client_socket.setblocking(False)
    client_socket.connect((host, port))
    client_socket.settimeout(timeout)
    connections[(host, port)] = client_socket

def send_hearbeat():
    for connection in connections.values():
        connection.send(b'hello, my name is han tyumi')
    

def loop():
    accept_clients()
    recv_clients()

connect_wifi()
new_connection(HOST, PORT, None)
while True:
    send_hearbeat()
    time.sleep(2)
