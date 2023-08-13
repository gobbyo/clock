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

    def __del__(self):
        print("__del__()")
        time.sleep(1)
        machine.reset() #reset to avoid OSError: [Errno 98] EADDRINUSE
    
    def _web_page(self):
      with uio.open(self.adminwebpage, 'r') as f:
        test = f.read()
        f.close()
      return test

    def _parseRequest(self,request):
        print("_parseRequest()")
        evalResponse = True
        lines = request.split('\r\n')
        for i in lines:
            if i.find('Referer:') == 0:
                query = i.split('http://' + self.url + '/')
                if len(query) > 1:
                    #['ssid=wifi','pwd=password','temp=on','humid=on','restart=on']
                    values = query[1].split(';')
                    print("write to secrets.py: {0}".format(values))
                    with uio.open('secrets.py', 'w') as f:         
                        for v in values:
                            t = v.split('=')
                            if len(t) > 1:
                                if v.find('restart=') == 0:
                                    restart = v.split('=')[1]
                                    if restart.find('on') == 0:
                                        evalResponse = False
                                else:
                                    f.write(t[0] + '="' + t[1] + '"\n')
                        f.flush()
                        f.close()
        return evalResponse
    
    def run(self):
        evalResponse = True
        gc.collect()

        # open soft wifi api mode
        wifi = network.WLAN(network.AP_IF)
        wifi.config(essid=self.hotspotssid,password=self.hotspotpassword,channel=self.channel)
        wifi.ifconfig([self.url, '255.255.255.0', self.url, '0.0.0.0'])
        wifi.active(True)
        while wifi.active() == False:
            pass

        print('Clock Hotspot is active')
        print(wifi.ifconfig())

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #creating socket object
        s.bind((self.url, 80))
        s.listen(5)
        while evalResponse:
            conn, addr = s.accept()
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024).decode('utf-8')
            #print('Content = %s' % str(request))
            evalResponse = self._parseRequest(request)
            response = self._web_page()
            conn.send(response)
            conn.close()
        wifi.active(False)
        wifi.disconnect()