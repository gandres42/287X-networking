from secrets import secrets
import wifi
import socketpool


TIMEOUT = None
HOST = '10.26.40.132'
PORT = 8080

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

print("Creating Socket")
with pool.socket(pool.AF_INET, pool.SOCK_STREAM) as s:
    s.settimeout(TIMEOUT)

    print("Connecting")
    s.connect((HOST, PORT))
    print("Sending")
    sent = s.send(b"Hello, world")
    print("Receiving")
    buff = bytearray(128)
    numbytes = s.recv_into(buff)
print(repr(buff))