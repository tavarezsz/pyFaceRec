from utils import *
import os

path = '../imagensChamada'
lista = os.listdir(path)
images = []
nomes = []

for im in lista:
    imgAtual = cv2.imread(f'{path}/{im}')
    images.append(imgAtual)
    # adiciona o nome da imagem sem o .jpeg
    nomes.append(os.path.splitext(im)[0])
print(nomes)

create_encode_file(images, 'turma01')