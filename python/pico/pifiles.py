import uos
import uio

def main():
    print(uos.listdir())
    with uio.open('test.txt', 'w') as f:
        f.write('"Hello World"')
        f.close()

    print(uos.stat('test.txt'))
    print("file len = {0}".format(uos.stat('test.txt')[6]))

    with uio.open('test.txt', 'r') as f:
        print(f.read())
        f.close()
    
    #uos.remove('test.txt')

if __name__ == "__main__":
    main()