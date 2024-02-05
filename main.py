import struct

def SaveTga(filename:str, width:int, height:int, bpp:int, data:list, vflip:bool) -> None:
    with open(filename, "wb") as f:
        f.write(struct.pack("<BBBHHBHHHHBB", 0, 0, 2, 0, 0, 0, 0, 0, width, height, bpp<<3, 0x0 if vflip else 0x20 ))
        for i in range (width*height):
            if i < len(data):
                f.write(struct.pack("<BBB", *data[i]))
            else:
                f.write(struct.pack("<BBB", 0,0,0))
        f.write(struct.pack("<BBBBBBBB", 0,0,0,0,0,0,0,0))
        f.write("TRUEVISION-XFILE.".encode())
        f.write(struct.pack("<B", 0))



data = [[0, 0, 128] for i in range (32)]
SaveTga("tmp.tga", 32, 32, 3, data, False)

from PIL import Image

#image = Image.frombytes('RGB', (128,128), data, 'raw')
image = Image.open("tmp.tga")
print(image)