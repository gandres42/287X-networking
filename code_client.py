from secrets import secrets
import wifi
import socketpool
import time
# 10.26.44.107

TIMEOUT = None
HOST = '10.26.46.142'
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

print(wifi.radio.ipv4_address)
pool = socketpool.SocketPool(wifi.radio)
s = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
s.setblocking(False)
s.connect((HOST, PORT))
s.settimeout(TIMEOUT)

print("Creating Socket")
while True:
    print("Sending")
    sent = s.send(b"Hello, world")
    time.sleep(2)