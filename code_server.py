from secrets import secrets
import wifi
import socketpool
import time
import errno

# 10.26.46.142

TIMEOUT = None
HOST = '10.26.40.132'
PORT = 8080
TIMEOUT = None
BUFSIZE = 64
clients = {}

connected = False
while not connected:
    print("Connecting to %s" % secrets["ssid"])
    try:
        wifi.radio.connect(secrets["ssid"], secrets["password"])
        print("Connected to %s!" % secrets["ssid"])
        connected = True
    except ConnectionError as e:
        print("Failed to connect to Wifi, trying again")

pool = socketpool.SocketPool(wifi.radio)
print("TCP Server at ", end="")
print(wifi.radio.ipv4_address)
s = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
s.settimeout(TIMEOUT)

s.bind(('0.0.0.0', PORT))
s.setblocking(False)
s.listen(16)
while True:
    try:
        conn, addr = s.accept()
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

    for client in clients.values():
        client['buf_pointer'] = client['buf_pointer'] + client['conn'].recv_into(memoryview(client['buf'])[client['buf_pointer']:], BUFSIZE - client['buf_pointer'])
        if client['buf_pointer'] == BUFSIZE:
            client['buf_pointer'] = 0
        print(client['addr'][0], end="")
        print(client['buf'])
        print(client['buf_pointer'])