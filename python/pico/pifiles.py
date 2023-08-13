import uos
import uio

def main():
    print(uos.listdir())
    #with uio.open('test.txt', 'w') as f:
    #    f.write('"Hello World"')
    #    f.close()

    #print(uos.stat('test.txt'))
    #print("file len = {0}".format(uos.stat('test.txt')[6]))

    with uio.open('admin.html', 'r') as f:
        page = ""
        line = ""
        while True:
            line = f.readline()
            if not line:
                break
            if line.find('<input type="text" id="url" value=>') > 0:
                line = '            <p><input type="text" id="url" value="' + "192.148.4.1" + '"> URL to hotspot</p>\n'
            page += line
        f.close()
        print(page)
    
    #uos.remove('test.txt')

if __name__ == "__main__":
    main()