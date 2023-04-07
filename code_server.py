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
MAXBUF = 256

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
print("Listening")
while True:
    try:
        conn, addr = s.accept()
        if conn:
            conn.settimeout(TIMEOUT)
            print("Accepted from", addr)
    except:
        pass
    
    