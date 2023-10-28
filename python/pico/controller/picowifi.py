import usocket as socket        #importing socket
import socket
import network            #importing network
import gc
import uio
import time
import config
import machine
import secrets

#purpose of this class is to bootstrap the PICO W connectivity by and setting the wifi ssid and password
#this class will also allow the user to set the temperature and humidity to be displayed on the pico
class hotspot:
    def __init__(self,ssid,password):
        self.url = '192.168.4.1'  #static ip address
        self.hotspotssid = ssid                  #Set access point name
        self.hotspotpassword = password      #Set your access point password
        self.adminwebpage = 'admin.html'
        self.completedsettings = 'completedsettings.html'
        self.channel = 11
        self.waittime = 10
        self.ssid = "ssid"
        self.pwd = "pwd"

    def __del__(self):
        print("__del__()")
        time.sleep(1)
        #machine.reset() #reset to avoid OSError: [Errno 98] EADDRINUSE
    
    def _writeSecrets(self,ssid,pwd):
        print("_secrets()")
        with uio.open('secrets.py', 'w') as f:
            f.write("usr='{0}'\r\npwd='{1}'".format(ssid,pwd))
            f.flush()
            f.close()

    def _web_page(self,htmlpage):
        conf = config.Config("config.json")
        tempCF = conf.read("tempCF")
        findCF = '<option value="{0}">'.format(conf.read("tempCF"))
        page = ""
        with uio.open(htmlpage, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if line.find('ssid') > 0:
                    line = line.replace('8eb5c1217eaf',secrets.usr)
                if line.find('pwd') > 0:
                    line = line.replace('fd3b61afb36d', secrets.pwd)
                if line.find('21:40') > 0:
                    s = conf.read("sleep")
                    line = line.replace('21:40','{0}:{1}'.format(s[0:2],s[2:4]))
                if line.find('480') > 0:
                    line = line.replace('480', conf.read("wake"))
                if line.find(findCF) > 0:
                    line = line.replace(findCF, '<option value="{0}" selected>'.format(tempCF))
                page += line
        f.close()
        return page

    def _requestPage(self,request):
        returnPage = 'UNKNOWN'
        #print('_requestPage request = {0}'.format(request))
        if request.find('admin') > 0:
            returnPage = 'admin'
        
        return returnPage

    def _parseRequest(self,request):
        print("_parseRequest()")
        conf = config.Config("")
        #titles=['ssid','pwd','temp','humid','restart']
        lines = request.split(';')
        for i in lines:
            t = i.split('=')
            if len(t) > 1:
                if t[1].find('?'):
                    t[1] = t[1].split('?')[0]
            #print('t = {0}'.format(t))
            if t[0] == 'ssid':
                self.ssid = t[1]
            if t[0] == 'pwd':
                self.pwd = t[1]
            if t[0] == 'tempCF':
                print('tempCF={0}'.format(t[1]))
                conf.write('tempCF',t[1])
            if t[0] == 'wake':
                print('wake={0}'.format(t[1]))
                conf.write('wake',t[1])
            if t[0] == 'sleep':
                s = t[1].split(':')
                print('sleep={0:04}'.format(s[0]+s[1]))
                conf.write('sleep',"{0:04}".format(s[0]+s[1]))
        self._writeSecrets(self.ssid,self.pwd)
    
    def connectWifi(self):
        wifi = network.WLAN(network.STA_IF)
        wifi.active(True)
        # set power mode to get WiFi power-saving off (if needed)
        wifi.config(pm = 0xa11140)
        print('self.hotspotssid={0},self.hotspotpassword={1}'.format(self.hotspotssid,self.hotspotpassword))
        wifi.connect(self.hotspotssid,self.hotspotpassword)
        print('wifi.isconnected({0})'.format(wifi.isconnected()))

        max_wait = self.waittime
        while max_wait > 0:
            if wifi.isconnected():
                #STAT_IDLE – no connection and no activity,
                #STAT_CONNECTING – connecting in progress,
                #STAT_WRONG_PASSWORD – failed due to incorrect password,
                #STAT_NO_AP_FOUND – failed because no access point replied,
                #STAT_CONNECT_FAIL – failed due to other problems,
                #STAT_GOT_IP – connection successful
                print('wifi.status() = {0}'.format(wifi.status()))
                self.url = wifi.ifconfig()[0]
                return True
            max_wait -= 1
            print('waiting for connection...')
            time.sleep(1)
        machine.reset()
        return False

    def connectAdmin(self):
        print('Clock Hotspot is starting')
        evalResponse = True
        gc.collect()

        # open soft wifi api mode
        wifi = network.WLAN(network.AP_IF)
        wifi.config(ssid='clock',password='12oclock',channel=self.channel,pm = 0xa11140)
        wifi.ifconfig([self.url, '255.255.255.0', self.url, '0.0.0.0'])
        wifi.active(True)
        i = self.waittime
        while (wifi.active() == False) and (i > 0):
            time.sleep(2)
            i -= 1
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
            print('connection request received = %s' % str(request))
            returnPage = self._requestPage(request)
            if returnPage == 'admin':
                print("admin response detected!")
                self._parseRequest(request)
                response = self._web_page(self.completedsettings)
                response_headers = {
                    'Content-Type': 'text/html; encoding=utf8',
                    'Content-Length': len(response)
                }
                response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                                        response_headers.items())

                # Reply as HTTP/1.1 server, saying "HTTP OK" (code 200).
                response_proto = 'HTTP/1.1'.encode()
                response_status = '200'.encode()
                response_status_text = 'OK'.encode() # this can be random

                conn.send(b'%s %s %s' % (response_proto, response_status,
                                                                response_status_text))
                conn.send(response_headers_raw.encode())
                conn.send(b'\n') # to separate headers from body
                conn.send(response.encode())
                time.sleep(3)
                conn.close()
                evalResponse = False
            else:
                response = self._web_page(self.adminwebpage)
                #print('response = {0}'.format(response))
                response_headers = {
                    'Content-Type': 'text/html; encoding=utf8',
                    'Content-Length': len(response)
                }
                response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in \
                                                        response_headers.items())

                # Reply as HTTP/1.1 server, saying "HTTP OK" (code 200).
                response_proto = 'HTTP/1.1'.encode()
                response_status = '200'.encode()
                response_status_text = 'OK'.encode() # this can be random

                conn.send(b'%s %s %s' % (response_proto, response_status,
                                                                response_status_text))
                conn.send(response_headers_raw.encode())
                conn.send(b'\n') # to separate headers from body
                conn.send(response.encode())

        wifi.disconnect()
        wifi.active(False)