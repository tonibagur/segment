from PIL import Image   

i = Image.open('imagen2.jpg')

i.crop((89,96,697,300)).save('test.jpg')

