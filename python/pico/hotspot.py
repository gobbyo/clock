import usocket as socket        #importing socket
import socket
import network            #importing network
import gc
import uio
import machine
import time

#purpose of this class is to bootstrap the PICO W connectivity by and setting the wifi ssid and password
#this class will also allow the user to set the temperature and humidity to be displayed on the pico
class hotspot:
    def __init__(self,ssid,password):
        self.url = '192.168.4.1'  #static ip address
        self.hotspotssid = ssid                  #Set access point name
        self.hotspotpassword = password      #Set your access point password
        self.adminwebpage = 'admin.html'
        self.channel = 11
        self.ssid = "ssid"
        self.pwd = "pwd"

    def __del__(self):
        print("__del__()")
        time.sleep(1)
        #machine.reset() #reset to avoid OSError: [Errno 98] EADDRINUSE
    
    def _web_page(self):
        page = ""
        line = ""
        with uio.open(self.adminwebpage, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('<p id="url"') > 0:
                        line = '        <p id="url" value="' + self.url + '" >hotspot address: ' + self.url + '</p>'  
                page += line
        f.close()
        return page

    def _parseRequest(self,request):
        print("_parseRequest()")
        evalResponse = True
        lines = request.split('\r\n')
        #titles=['ssid','pwd','temp','humid','restart']
        for i in lines:
            if i.find('Referer:') == 0:
                query = i.split('http://' + self.url + '/')
                if len(query) > 1:
                    values = query[1].split(';')
                    with uio.open('config.py', 'w') as f:         
                        for v in values:
                            t = v.split('=')
                            if len(t) > 1:
                                if t[0].find('restart') >= 0:
                                    if t[1].find('on') >= 0:
                                        evalResponse = False
                                if t[0].find('ssid') >= 0:
                                    self.ssid = t[1]
                                    #f.write('ssid="' + t[1] + '"\n')
                                if t[0].find('pwd') >= 0:
                                    self.pwd = t[1]
                                    #f.write('pwd="' + t[1] + '"\n')
                                else:
                                    f.write(t[0] + '="' + t[1] + '"\n')
                                    print("writing to config.py: {0}={1}".format(t[0],t[1]))
                        f.flush()
                        f.close()
        return evalResponse
    
    def run(self):
        print('Clock Hotspot is starting')
        evalResponse = True
        gc.collect()

        # open soft wifi api mode
        wifi = network.WLAN(network.AP_IF)
        wifi.config(essid=self.hotspotssid,password=self.hotspotpassword,channel=self.channel,pm = 0xa11140)
        wifi.ifconfig([self.url, '255.255.255.0', self.url, '0.0.0.0'])
        wifi.active(True)
        i = 0
        while wifi.active() == False:
            time.sleep(1)
            i += 1
            print("Waiting for WiFi AP to be active, attempt {0}".format(i))
            pass

        print('Clock Hotspot is active')
        print(wifi.ifconfig())
        self.url = wifi.ifconfig()[0]

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #creating socket object
        s.bind((self.url, 80))
        s.listen(5)
        while evalResponse:
            conn, addr = s.accept()
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024).decode('utf-8')
            print('Content = %s' % str(request))
            evalResponse = self._parseRequest(request)
            response = self._web_page()
            conn.send(response)
            conn.close()
        wifi.active(False)
        wifi.disconnect()