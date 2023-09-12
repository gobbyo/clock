import uio

class logger():
    totalsize = 0
    filename = ""

    def __init__(self, filename, sizeinbytes = 1024):
        self.totalsize = int(sizeinbytes)
        if filename == "":
            self.filename = "log.txt"
        else:
            self.filename = filename
        
        with uio.open(self.filename, "w") as f:
            f.write("")
            f.close()
    
    def __del__(self):
        pass
    
    def write(self,value):
        buffer = ""
        with uio.open(self.filename, "r") as f:
            buffer = f.read()
            f.close()
        with uio.open(self.filename, "w") as f:
            buffer + "\r\n{0}".format(value)
            print(value)
            if len(buffer) < self.totalsize:
                f.write(buffer + "\r\n{0}".format(value))
            else:
                f.write("\r\n{0}".format(value))
            f.flush()
            f.close()