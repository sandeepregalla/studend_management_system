import qrcode
url =input("Enter your url:")
filename =input("filename you want to save it as : ")

if not filename.endswith(".png"):
    filename = filename +".png"

img = qrcode.make(url)
img.save(filename) 