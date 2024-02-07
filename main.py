import struct
from io import BufferedWriter
from io import BufferedReader

class TgaFile:

    class TgaColor:
        def __init__(self, b:int = 0, g:int = 0, r:int = 0, a:int = 0):
            self.r = r
            self.g = g
            self.b = b
            self.a = a

        def get1Byte(self):
            return struct.pack("<B", self.b)
        
        def get3Bytes(self):
            return struct.pack("<BBB", self.b, self.g, self.r)

        def get4Bytes(self):
            return struct.pack("<BBBB", self.b, self.g, self.r, self.a)
        
        def set(self, b:int = 0, g:int = 0, r:int = 0, a:int = 0):
            self.r = r
            self.g = g
            self.b = b
            self.a = a
        
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

    @staticmethod
    def LoadTga(filename:str):
        tgaFile = None
        with open(filename, "rb") as f:
            header = struct.unpack("<BBBHHBHHHHBB", f.read(18))
            if header[0] != 0 or header[1] != 0 or header[3] != 0 or header[4] != 0 or header[5] != 0 or header[6] != 0 or header[7] != 0:
                return None
            datatype = header[2]
            width = header[8]
            height = header[9]
            bytesPerPixel = header[10] >> 3
            vflip = not ((header[10] & 0x20) == 0x20)
            hflip = ((header[10] & 0x10) == 0x10)
            rle = False

            if width <= 0 or height <= 0 or (bytesPerPixel != 4 and bytesPerPixel != 3 and bytesPerPixel != 1):
                return None
            
            tgaFile = TgaFile(width, height, bytesPerPixel)

            if (bytesPerPixel == 1 and datatype == 11) or (bytesPerPixel != 1 and datatype == 10):
                rle = True
            elif (bytesPerPixel == 1 and datatype != 3) or (bytesPerPixel != 1 and datatype != 2):
                return None
            if rle:
                tgaFile.LoadRLEData(f)
            else:
                tgaFile.LoadRawData(f)
            if vflip:
                tgaFile.FlipVertically()
            if hflip:
                tgaFile.FlipHorizontally()
        return tgaFile
            
    def LoadRLEData(self, fileObj:BufferedReader):
            pixelCount = self.width * self.height
            currentPixel = 0
            currentByte  = 0
            while currentPixel < pixelCount:
                chunkHeader = struct.unpack("<B", fileObj.read(1))[0]

                if chunkHeader < 128:
                    chunkHeader += 1
                    if self.bpp == 1:
                        for i in range (chunkHeader):
                            self.data[currentPixel + i].set(*struct.unpack("<B", fileObj.read(1)))
                    elif self.bpp == 3:
                        for i in range (chunkHeader):
                            self.data[currentPixel + i].set(*struct.unpack("<BBB", fileObj.read(3)))
                    elif self.bpp == 4:
                        for i in range (chunkHeader):
                            self.data[currentPixel + i].set(*struct.unpack("<BBBB", fileObj.read(4)))
                    currentPixel += chunkHeader
                else:
                    chunkHeader -= 127
                    if self.bpp == 1:
                        color = struct.unpack("<B", fileObj.read(1))
                    elif self.bpp == 3:
                        color = struct.unpack("<BBB", fileObj.read(3))
                    elif self.bpp == 4:
                        color = struct.unpack("<BBBB", fileObj.read(4))
                    for i in range (chunkHeader):
                        self.data[currentPixel + i].set(*color)
                    currentPixel += chunkHeader

    def LoadRawData(self, fileObj:BufferedReader):
        if self.bpp == 1:
            for i in range (self.width*self.height):
                self.data[i].set(*struct.unpack("<B", fileObj.read(1)))
        elif self.bpp == 3:
            for i in range (self.width*self.height):
                self.data[i].set(*struct.unpack("<BBB", fileObj.read(3)))
        elif self.bpp == 4:
            for i in range (self.width*self.height):
                self.data[i].set(*struct.unpack("<BBBB", fileObj.read(4)))


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

    def FlipHorizontally(self):
        for row in range(self.height):
            rowOffset = row * self.height
            for column in range(self.width//2):
                cell1 = rowOffset + column
                cell2 = rowOffset + self.width - 1 - column
                self.data[cell1], self.data[cell2] = self.data[cell2], self.data[cell1]

    def FlipVertically(self):
        for row in range(self.height//2):
            rowOffset1 = row * self.height
            rowOffset2 = (self.height - 1 - row) * self.height
            for column in range(self.width):
                cell1 = rowOffset1 + column
                cell2 = rowOffset2 + column
                self.data[cell1], self.data[cell2] = self.data[cell2], self.data[cell1]

file = TgaFile(32, 32, 3)
file.Put(0, 0, 255, 0, 0)
file.Put(31, 31, 0, 255, 0)
file.SaveTga("tmp.tga", False, True)

file2 = TgaFile.LoadTga("tmp.tga")
file2.SaveTga("tmp2.tga", False, False)


#from PIL import Image

#image = Image.frombytes('RGB', (128,128), data, 'raw')
# image = Image.open("tmp.tga")
# print(image)