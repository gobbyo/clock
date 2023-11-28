import usocket as socket        #importing socket
import socket
import network            #importing network
import gc
import uio
import time
import config
import machine
import secrets
import kineticDisplay

#purpose of this class is to bootstrap the PICO W connectivity by and setting the wifi ssid and password
#this class will also allow the user to set the temperature and humidity to be displayed on the pico
class hotspot:
    def __init__(self,ssid,password):
        self.url = '192.168.4.1'  #static ip address
        self.hotspotssid = ssid                  #Set access point name
        self.hotspotpassword = password      #Set your access point password
        self.adminwebpage = 'admin.html'
        self.completedsettings = 'completedsettings.html'
        self.digitpage = 'digit.html'
        self.channel = 11
        self.waittime = 10
        self.ssid = "ssid"
        self.pwd = "pwd"
        self.currentDigit = -1
        self.extendAngles = []
        self.retractAngles = []

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

    def _admin_page(self):
        page = ''
        conf = config.Config("config.json")
        tempCF = conf.read("tempCF")
        findCF = '<option value="{0}">'.format(conf.read("tempCF"))
        with uio.open(self.adminwebpage, 'r') as f:
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

    def _digit_page(self, display):
        page = 'Error reading extend and retract angles for digit {0}'.format(self.currentDigit)
        
        self.extendAngles = display.getExtendAngles(self.currentDigit)
        print('extendAngles = {0}  len(extendAngles) = {1}'.format(self.extendAngles,len(self.extendAngles)))
        self.retractAngles = display.getRetractAngles(self.currentDigit)
        print('retractAngles = {0}  len(retractAngles) = {1}'.format(self.retractAngles,len(self.retractAngles)))
        if len(self.extendAngles) == 7 and len(self.retractAngles) == 7:
            with uio.open(self.digitpage, 'r') as f:
                page = ''
                while True:
                    line = f.readline()
                    if not line:
                        break
                    if line.find('<h1>Digit 0 Settings</h1>') > 0:
                        line = '<h1>Digit {0} Settings</h1>'.format(self.currentDigit)
                    if line.find('<td><input type="number" id="aExtend" value="10" min="0" max="30"></td>') > 0:
                        line = '<td><input type="number" id="aExtend" value="{0}" min="0" max="30"></td>'.format(self.extendAngles[0])
                    if line.find('<td><input type="number" id="bExtend" value="10" min="0" max="30"></td>') > 0:
                        line = '<td><input type="number" id="bExtend" value="{0}" min="0" max="30"></td>'.format(self.extendAngles[1])
                    if line.find('<td><input type="number" id="cExtend" value="10" min="0" max="30"></td>') > 0:
                        line = '<td><input type="number" id="cExtend" value="{0}" min="0" max="30"></td>'.format(self.extendAngles[2])
                    if line.find('<td><input type="number" id="dExtend" value="10" min="0" max="30"></td>') > 0:
                        line = '<td><input type="number" id="dExtend" value="{0}" min="0" max="30"></td>'.format(self.extendAngles[3])
                    if line.find('<td><input type="number" id="eExtend" value="10" min="0" max="30"></td>') > 0:
                        line = '<td><input type="number" id="eExtend" value="{0}" min="0" max="30"></td>'.format(self.extendAngles[4])
                    if line.find('<td><input type="number" id="fExtend" value="10" min="0" max="30"></td>') > 0:
                        line = '<td><input type="number" id="fExtend" value="{0}" min="0" max="30"></td>'.format(self.extendAngles[5])
                    if line.find('<td><input type="number" id="gExtend" value="10" min="0" max="30"></td>') > 0:
                        line = '<td><input type="number" id="gExtend" value="{0}" min="0" max="30"></td>'.format(self.extendAngles[6])
            
                    if line.find('<td><input type="number" id="aRetract" value="100" min="80" max="120"></td>') > 0:
                        line = '<td><input type="number" id="aRetract" value="{0}" min="80" max="120"></td>'.format(self.retractAngles[0])
                    if line.find('<td><input type="number" id="bRetract" value="100" min="80" max="120"></td>') > 0:
                        line = '<td><input type="number" id="bRetract" value="{0}" min="80" max="120"></td>'.format(self.retractAngles[1])
                    if line.find('<td><input type="number" id="cRetract" value="100" min="80" max="120"></td>') > 0:
                        line = '<td><input type="number" id="cRetract" value="{0}" min="80" max="120"></td>'.format(self.retractAngles[2])
                    if line.find('<td><input type="number" id="dRetract" value="100" min="80" max="120"></td>') > 0:
                        line = '<td><input type="number" id="dRetract" value="{0}" min="80" max="120"></td>'.format(self.retractAngles[3])
                    if line.find('<td><input type="number" id="eRetract" value="100" min="80" max="120"></td>') > 0:
                        line = '<td><input type="number" id="eRetract" value="{0}" min="80" max="120"></td>'.format(self.retractAngles[4])
                    if line.find('<td><input type="number" id="fRetract" value="100" min="80" max="120"></td>') > 0:
                        line = '<td><input type="number" id="fRetract" value="{0}" min="80" max="120"></td>'.format(self.retractAngles[5])
                    if line.find('<td><input type="number" id="gRetract" value="100" min="80" max="120"></td>') > 0:
                        line = '<td><input type="number" id="gRetract" value="{0}" min="80" max="120"></td>'.format(self.retractAngles[6])
                    
                    if line.find('var query = "digit0"') > 0:
                        line = 'var query = "digit{0}"'.format(self.currentDigit)
                    page += line
                f.close()
        return page
    
    def parseAngleSettings(self, request):
        print("parseAngleSettings()")
        lines = request.split(';')
        for i in lines:
            t = i.split('=')
            if len(t) > 1:
                if t[1].find('?'):
                    t[1] = t[1].split('?')[0]
            if t[0] == 'aExtend':
                self.extendAngles[0] = int(t[1])
            if t[0] == 'bExtend':
                self.extendAngles[1] = int(t[1])
            if t[0] == 'cExtend':
                self.extendAngles[2] = int(t[1])
            if t[0] == 'dExtend':
                self.extendAngles[3] = int(t[1])
            if t[0] == 'eExtend':
                self.extendAngles[4] = int(t[1])
            if t[0] == 'fExtend':
                self.extendAngles[5] = int(t[1])
            if t[0] == 'gExtend':
                self.extendAngles[6] = int(t[1])
            if t[0] == 'aRetract':
                self.retractAngles[0] = int(t[1])
            if t[0] == 'bRetract':
                self.retractAngles[1] = int(t[1])
            if t[0] == 'cRetract':
                self.retractAngles[2] = int(t[1])
            if t[0] == 'dRetract':
                self.retractAngles[3] = int(t[1])
            if t[0] == 'eRetract':
                self.retractAngles[4] = int(t[1])
            if t[0] == 'fRetract':
                self.retractAngles[5] = int(t[1])
            if t[0] == 'gRetract':
                self.retractAngles[6] = int(t[1])

    def _completed_page(self):
        page = ''
        with uio.open(self.completedsettings, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                page += line
            f.close()
        return page
    
    def _requestPage(self,request):
        returnPage = 'admin'
        i = request.find('\n')
        if i < 0:
            i = request.find('\r')
        if i >= 0:
            req = request[0:i]
            print('_requestPage() {0}'.format(req))
            if req.find('admin') > 0:
                returnPage = 'admin'
            if req.find('digit') > 0:
                returnPage = 'digit'
            if req.find('anglesettings') > 0:
                returnPage = 'anglesettings'
            if req.find('wifisettings') > 0:
                returnPage = 'wifisettings'
        
        return returnPage

    def parseAdminSettings(self,request):
        print("parseAdminSettings()")
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
    
    def sendreply(self,conn, pagebuffer):
        print("sendreply(conn={0})".format(conn))
        response_headers = {
            'Content-Type': 'text/html; encoding=utf8',
            'Content-Length': len(pagebuffer)
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
        conn.send(pagebuffer.encode())

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

    def connectAdmin(self, display):
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
            if returnPage == 'wifisettings':
                print("update to wifisettings detected!")
                self.parseAdminSettings(request)
                pagebuffer = self._completed_page()
                self.sendreply(conn,pagebuffer)
                time.sleep(1)
                conn.close()
                evalResponse = False
            if returnPage == 'anglesettings':
                print("update to anglesettings detected! request={0}".format(request))
                self.parseAngleSettings(request)
                display.setAngles(self.currentDigit, self.extendAngles, self.retractAngles)
                pagebuffer = self._admin_page()
                self.sendreply(conn,pagebuffer)
            if returnPage == 'digit':
                i = request.find('digit') + len('digit')
                print("digit page detected! Digit={0}".format(request[i]))
                if request[i].isdigit():
                    self.currentDigit = request[i]
                    pagebuffer = self._digit_page(display)
                    self.sendreply(conn,pagebuffer)
            if returnPage == 'admin':
                pagebuffer = self._admin_page()
                self.sendreply(conn,pagebuffer)

        wifi.disconnect()
        wifi.active(False)