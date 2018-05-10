from PIL import Image

img = Image.open('test.jpg')
size = (100, 73)
print("썸네일 전 %s " % str(img.size))
img.thumbnail(size)
img.save('test3.jpg')
print("썸네일 후 %s " % str(img.size))
print(img.format)




