from utils import *
import os

path = '../teste'
lista = os.listdir(path)
images = []
nomes = []

for im in lista:
    imgAtual = cv2.imread(f'{path}/{im}')
    images.append(imgAtual)
    # adiciona o nome da imagem sem o .jpeg
    nomes.append(os.path.splitext(im)[0])
print(nomes)

#create_encode_file(images, 'turma02')
#tt = findEncoding(images)

#conn = conectar_db()

# atualizar_presenca_db('chamada02', conn, 'EDUARDO')

#findEncoding()
conn = conectar_db()

abrir_chamada('turma01', ler_chamada(), conn)