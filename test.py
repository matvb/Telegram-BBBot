import os
import glob
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

bialfotos = list()
for foto in glob.glob(THIS_FOLDER+ '/img/*.JPG'):
    print('hi')
    im = open(foto, 'rb')
    bialfotos.append(im)
    print(foto)

boninhofotos = list()
for foto in glob.glob('./img/boninho*.jpg'): #
    im = open(foto, 'rb')
    boninhofotos.append(im)

premioFotos = list()
for foto in glob.glob('./img/premio*.jpg'): #
    im = open(foto, 'rb')
    premioFotos.append(im)

print(bialfotos[0])
