import SimpleCV

i=SimpleCV.Image('static/uploads/image_3.jpg')
i2=i.edges()
i2.save('datasets/edges.jpg')

