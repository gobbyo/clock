import uos
import uio

def main():
    evalResponse = True
    values=['undefinedssid=Clipper', 'pwd=Orcatini', 'temp=on', 'humid=on', 'restart=on?']
    for v in values:
        t = v.split('=')
        print(t)
        if t[0].find('restart') == 0:
            if t[1].find('on') == 0:
                evalResponse = False
                print("evalResponse = False")
        if t[0].find('undefinedssid') == 0:
            print('ssid="' + t[1] + '"\n')
        else:
            print(t[0] + '="' + t[1] + '"\n')
    
    #uos.remove('test.txt')

if __name__ == "__main__":
    main()