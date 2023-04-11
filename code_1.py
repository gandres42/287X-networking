from secrets import secrets
import wifi
import socketpool
import time
import errno

# used only for testing & demonstration
CLIENT_IP = "10.26.43.108"
SERVER_IP = "10.26.43.61"

BUFSIZE = 64

connections = {}
server_socket = None
accepting = False

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
    global server_socket
    print("TCP Server at ", end="")
    print(wifi.radio.ipv4_address)
    pool = socketpool.SocketPool(wifi.radio)
    server_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.settimeout(timeout)
    server_socket.setblocking(False)
    server_socket.listen(16)
    accepting = True

def accept_clients():
    global server_socket
    try:
        sock, addr = server_socket.accept()
        if sock:
            sock.settimeout(None)
            print("Accepted from", addr)
            connections[addr] = {
                'sock': sock,
                'buf': bytearray([0] * BUFSIZE),
                'addr': addr,
                'buf_pointer': 0,
                'keepalive': time.monotonic
            }
    except:
        pass



def recv():
    for client in connections.values():
        i = client['sock'].recv_into(memoryview(client['buf'])[client['buf_pointer']:], BUFSIZE - client['buf_pointer'])
        client['buf_pointer'] = client['buf_pointer'] + i
        if client['buf_pointer'] == BUFSIZE:
            client['buf_pointer'] = 0
        if i != 0:
            print(client['buf'])
        # decoded_buffer = client['buf'].decode()

def broadcast():
    for client in connections.values():
        client['sock'].send("hello")

def new_connection(host, port, timeout):
    if (host, port) in connections.keys():
        return
   
    pool = socketpool.SocketPool(wifi.radio)
    new_sock = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    new_sock.setblocking(False)
    new_sock.settimeout(timeout)
    connected = False
    while not connected:
        print("Connecting to " + host)
        try:
            new_sock.connect((host, port))
            connected = True
        except:
            pass
    print("Connected to " + host)
    connections[(host, port)] = {
        'sock': new_sock,
        'buf': bytearray([0] * BUFSIZE),
        'addr': host,
        'buf_pointer': 0,
        'keepalive': time.monotonic
    }
    
def loop():
    if accepting:
        accept_clients()
    

connect_wifi()

# print(str(wifi.radio.ipv4_address))
# if str(wifi.radio.ipv4_address) == SERVER_IP:
#     print("I am the server!")
#     start_accepting('0.0.0.0', 8080, None)
# elif str(wifi.radio.ipv4_address) == CLIENT_IP:
#     print("I am the client!")
#     init_client(SERVER_IP, 8080, None)
#     while True:

#         # hearbeat()
#         # time.sleep(1)

