import uio
import ujson

class Config():
    def __init__(self, filename):
        if filename == "":
            self.filename = "config.json"
        else:
            self.filename = filename
    
    def __del__(self):
        pass

    def read(self,name):
        c = ""
        with uio.open(self.filename, "r") as f:
            c = ujson.load(f)
            f.close()
        return c[name]
    
    def write(self,name,value):
        c = ""
        with uio.open(self.filename, "r") as f:
            c = ujson.load(f)
            f.close()
        with uio.open(self.filename, "w") as f:
            c[name] = value
            ujson.dump(c, f)
            f.flush()
            f.close()