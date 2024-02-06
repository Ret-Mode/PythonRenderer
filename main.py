import struct
from io import BufferedWriter

class TgaFile:

    class TgaColor:
        def __init__(self, r:int = 0, g:int = 0, b:int = 0, a:int = 0):
            self.r = r
            self.g = g
            self.b = b
            self.a = a

        def get1Byte(self):
            return struct.pack("<B", self.r)
        
        def get3Bytes(self):
            return struct.pack("<BBB", self.b, self.g, self.r)

        def get4Bytes(self):
            return struct.pack("<BBBB", self.b, self.g, self.r, self.a)
        
        def __eq__(self, value: "TgaFile.TgaColor") -> bool:
            return self.r == value.r and self.g == value.g and self.b == value.b and self.a == value.a
        
    def __init__(self, width:int, height:int, bytesPerPixel:int):
        self.width = width
        self.height = height
        self.bpp = bytesPerPixel
        self.data = [self.TgaColor() for i in range (width*height)]

    def SaveRawData(self, fileObj:BufferedWriter):
        if self.bpp == 1:
            for i in range (self.width*self.height):
                fileObj.write(self.data[i].get1Byte())
        elif self.bpp == 3:
            for i in range (self.width*self.height):
                fileObj.write(self.data[i].get3Bytes())
        elif self.bpp == 4:
            for i in range (self.width*self.height):
                fileObj.write(self.data[i].get4Bytes())

    def SaveRLEData(self, fileObj:BufferedWriter):
        maxChunkLength = 128
        nPixels = self.width * self.height
        currentPixel = 0
        while currentPixel < nPixels:
            runLength = 1
            raw = True
            while (currentPixel + runLength < nPixels) and (runLength < maxChunkLength):
                succEq = self.data[currentPixel] == self.data[currentPixel + runLength]
                if runLength == 1:
                    raw = not succEq
                if succEq and raw:
                    runLength -= 1
                    break
                if not raw and not succEq:
                    break
                runLength += 1
            if raw:
                fileObj.write(struct.pack("<B",runLength-1))
            else:
                fileObj.write(struct.pack("<B",runLength+127))

            if self.bpp == 1:
                if raw:
                    for i in range(runLength):
                        fileObj.write(self.data[currentPixel + i].get1Byte())
                else:
                    fileObj.write(self.data[currentPixel].get1Byte())
            elif self.bpp == 3:
                if raw:
                    for i in range(runLength):
                        fileObj.write(self.data[currentPixel + i].get3Bytes())
                else:
                    fileObj.write(self.data[currentPixel].get3Bytes())
            elif self.bpp == 4:
                if raw:
                    for i in range(runLength):
                        fileObj.write(self.data[currentPixel + i].get4Bytes())
                else:
                    fileObj.write(self.data[currentPixel].get4Bytes())

            currentPixel += runLength

    def SaveTga(self, filename:str, vflip:bool=False, rle:bool=False) -> None:
        with open(filename, "wb") as f:
            f.write(self.GetHeader(vflip, rle))
            if rle:
                self.SaveRLEData(f)
            else:
                self.SaveRawData(f)
            f.write(self.GetFooter())

    def GetHeader(self, vflip:bool = False, rle:bool=False):
        datatype = 1 if self.bpp == 1 else 0
        datatype = datatype + (10 if rle else 2)
        return struct.pack("<BBBHHBHHHHBB", 0, 0, datatype, 0, 0, 0, 0, 0, self.width, self.height, self.bpp<<3, 0x0 if vflip else 0x20 )

    def GetFooter(self):
        return struct.pack("<BBBBBBBB", 0,0,0,0,0,0,0,0) + "TRUEVISION-XFILE.".encode() + struct.pack("<B", 0)

    def Put(self, x:int, y:int, r:int=0, g:int=0, b:int=0, a:int=0):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[x*self.width + y] = TgaFile.TgaColor(r, g, b, a)

file = TgaFile(32, 32, 4)
file.Put(0, 0, 255, 0, 0)
file.Put(31, 31, 0, 255, 0)
file.SaveTga("tmp.tga", False, True)

from PIL import Image

#image = Image.frombytes('RGB', (128,128), data, 'raw')
image = Image.open("tmp.tga")
print(image)