from secrets import secrets
import wifi
import socketpool
import time
import errno
import random
# import json

# used only for testing & demonstration
CLIENT_IP = "10.26.40.218"
SERVER_IP = "10.26.42.121"

BUFSIZE = 128

socket = None
last_recv = 0
last_send = 0 
buffer = bytearray([0] * BUFSIZE)
buf_pointer = 0

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

def start_server(host, port, timeout):
    global socket, last_recv
    print("Accepting connections at ", end="")
    print(wifi.radio.ipv4_address)
    pool = socketpool.SocketPool(wifi.radio)
    socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    socket.bind((host, port))
    socket.listen(255)
    socket, addr = socket.accept()
    socket.settimeout(timeout)
    last_recv = time.monotonic()
    time.sleep(1)
    print("Accepted from", addr)

def recv():
    global socket, last_recv, last_send, buffer, buf_pointer
    try:
        # socket.recv_into(buffer, BUFSIZE)
        i = socket.recv_into(memoryview(buffer)[buf_pointer:], BUFSIZE - buf_pointer)
        last_recv = time.monotonic()
        buf_pointer = buf_pointer + i
        if buf_pointer == BUFSIZE:
            buf_pointer = 0
        print(buffer)
    except Exception as e:
        pass

def new_connection(host, port, timeout):
    global socket, last_recv
    pool = socketpool.SocketPool(wifi.radio)
    socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    socket.connect((host, port))
    socket.settimeout(timeout)
    last_recv = time.monotonic()
    time.sleep(1)

def heartbeat():
    global socket, last_recv, last_send
    if time.monotonic() - last_recv > 5:
        print("client disconnected!")
        return False
    try:
        socket.send(b'{still alive}')
        return True
    except Exception as e:
        return True

connect_wifi()
print(str(wifi.radio.ipv4_address))
if str(wifi.radio.ipv4_address) == SERVER_IP:
    print("I am the server!")
    start_server('0.0.0.0', 8080, 1)
    while heartbeat():
        recv()
elif str(wifi.radio.ipv4_address) == CLIENT_IP:
    print("I am the client!")
    new_connection(SERVER_IP, 8080, 1)
    while heartbeat():
        recv()