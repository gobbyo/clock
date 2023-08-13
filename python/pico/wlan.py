import network
import socket
from time import sleep
import machine
import secretsstash
import urequests as requests
import ujson

class incoming_request:
    def __init__(self, data):
        self.data = data.decode('utf-8')
        self.method = ''
        self.url = ''
        self.headers = {}
        self.body = ''
        self.parse()

    def parse(self):
        lines = self.data.split('\r\n')
        self.method, self.url, _ = lines[0].split(' ')
        for lines in lines[1:]:
            if lines == '':
                break
            key, value = lines.split(': ')
            print("{0}:{1}".format(key, value))
            self.headers[key] = value
        self.body = self.data.split('\r\n\r\n')[1]

    def __repr__(self):
        return self.data

def connect_to_wifi(wlan):
    wlan.active(True)
    wlan.connect(secretsstash.ssid, secretsstash.password)
    i = 0
    while wlan.isconnected() == False and i < 10:
        print('Waiting for connection...')
        sleep(1)
        i += 1
    
    print(wlan.ifconfig())

def main():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    connect_to_wifi(wlan)

    s = socket.socket()
    # Bind the socket to port 80
    s.bind(('', 80))
    # Set the socket to listen for connections
    s.listen(5)
    # Create a loop to accept and handle connections
    try:
        while True:                             
            # Accept a connection from a client
            conn, addr = s.accept()
            print('Connection from', addr)

            # Read the data sent by the client
            data = conn.recv(1024)
            print('Data received:', data)
            d = incoming_request(data)
            print('Data received:', d.body)

            j = ujson.loads(d.body)
            with open('secretsstash.py', 'w') as f:
                f.write("ssid='{0}'\n".format(j['ssid']))
                f.write("password='{0}'\n".format(j['password']))
                f.close()
            sleep(3)
            reply = "HTTP/1.1 200 OK\r\nCache-Control: no-cache, private\r\nContent-Length: 107\r\nDate: Mon, 24 Nov 2014 10:21:21 GMT\r\n\r\n"
            buf = bytearray(len(reply))
            buf = reply.encode('utf-8')
            s.send(buf)

            # Close the connection
            conn.close()

            connect_to_wifi()

    except KeyboardInterrupt:
        machine.reset()
    finally:
        s.close()
        wlan.disconnect()
        wlan.active(False)

if __name__ == "__main__":
    main()