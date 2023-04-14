from secrets import secrets
import wifi
import asyncio
import socketpool

CLIENT_IP = "10.26.40.218"
SERVER_IP = "10.26.42.121"

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

async def connect(host, port):
    pool = socketpool.SocketPool(wifi.radio)
    new_sock = await asyncio.run(pool.socket(pool.AF_INET, pool.SOCK_STREAM))
    new_sock.settimeout(None)
    new_sock.setblocking(False)

async def accept_clients():
    pool = socketpool.SocketPool(wifi.radio)
    server_socket = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8080))
    server_socket.settimeout(None)
    server_socket.listen(16)

    print("why")

    while True:
        try:
            print("test")
            sock, addr = await asyncio.run(server_socket.accept())
            print("Accepted from", addr)
        except:
            pass


connect_wifi()
print(wifi.radio.ipv4_address)

if str(wifi.radio.ipv4_address) == SERVER_IP:
    accept_clients()
    print("I am a server")
elif str(wifi.radio.ipv4_address) == CLIENT_IP:
    connect(SERVER_IP, 8080)
    print("I am a client")

while True:
    pass