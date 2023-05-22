import cv2
import numpy as np
import face_recognition
import os
import pandas as pd
from datetime import datetime, timedelta
# import mysql.connector
from flask import Flask, jsonify, request
import utils

path = 'imagensChamada'
images = []
nomes = []
lista = os.listdir(path)


""""
df = pd.read_csv("C:\\Users\\luisw\\OneDrive\\Área de Trabalho\\TCC\\pyFaceRec\\listaChamada.csv")
try:
    connection = mysql.connector.connect(host='localhost',
                                         database='rest-api',
                                         user='root',
                                         password='1234')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Conectado ao servidor MySQL: versão", db_Info)
except Error as e:
    print("Erro ao conectar ao MySQL", e)
cursor = connection.cursor()
for index, row in df.iterrows():
    sql = "INSERT INTO chamadaAlunos (nome, entrada, saida, status) VALUES (%s, %s, %s, %s)"
    val = (row['nome'], row['entrada'], row['saida'], row['status'])
    cursor.execute(sql, val)
    connection.commit()
print(cursor.rowcount, "registros inseridos com sucesso.")
cursor.close()
connection.close()
print("Conexão com o MySQL encerrada.")
"""
#cria lista com os nomes que já estão na chamada e verifica quem já saiu
with open('listaChamada.csv', 'r') as f:
    listaStatus = []
    listaChamada = f.readlines()
    listaNomes = []
    listaSaiu = []
    # preenche as lsitas de acordo com o estado atual da chamada
    # garante que se o app for parado a lista de chamada não reinicie
    for line in listaChamada:
        # separa cada ',' em colunas
        entrada = line.split(',')
        # se não tiver hora de saida na lista
        if entrada[-2].strip() != '-':
            listaSaiu.append(entrada[0])


        listaNomes.append(entrada[0])
        if entrada[-1].strip() != '-' and entrada[-1].strip() != 'status':
            status = entrada[-1].strip()
            if status == 'presente(atraso)':
                listaStatus.append([entrada[0], 1])
            elif status == 'presente(parcial)':
                listaStatus.append([entrada[0], 2])
            elif status == 'presente':
                listaStatus.append([entrada[0], 3])
            else:
                listaStatus.append([entrada[0], 0])
    f.close()

# ler cada imagem da lista
for im in lista:
    imgAtual = cv2.imread(f'{path}/{im}')
    images.append(imgAtual)
    # adiciona o nome da imagem sem o .jpeg
    nomes.append(os.path.splitext(im)[0])
print(nomes)


def load_configs():
    with open("interface/configuracoes.txt", "r") as file:
        lines = [line.rstrip() for line in file]

        # pega só o valor numérico de cada linha
        entrada = lines[0].split()[2]
        saida = lines[1].split()[2]
        tolerancia = lines[2].split()[2]
        # fechamento = lines[3].strip()[2]

        try:
            dt_entrada = datetime.strptime(entrada, "%H:%M:%S")
            dt_saida = datetime.strptime(saida, "%H:%M:%S")
            # dt_fechamento = datetime.strptime(fechamento, "%H:%M:%S")
        except ValueError:
            print("[ERRO]valores de configuração fora do formato HH/MM/SS")
        else:
            return dt_entrada, dt_saida, tolerancia


entrada, saida, tolerancia = load_configs()

tolerancia = int(tolerancia)
# adiciona os minutos de tolerancia ao tempo de entrada
hr_atraso = entrada + timedelta(minutes=tolerancia)
# fechamento = fechamento.time()
entrada = entrada.time()
saida = saida.time()

def AtualizarStatus(nome):

    pds = pd.read_csv("listaChamada.csv")
    nome_index = listaNomes.index(nome) - 1
    status = listaStatus[nome_index]
    msg = 'ausente'
    if status[1] == 1:
        msg = 'presente(atraso)'
    elif status[1] == 2:
        msg = 'presente(parcial)'
    elif status[1] == 3:
        msg = 'presente'

    with open('listaChamada.csv', 'a') as file:
        pds.loc[nome_index, 'status'] = msg
        pds.to_csv("listaChamada.csv", index=False)
    file.close()

def fecharChamada():
    """
    Adicona os alunos que não fizeram a chamada como ausentes

    :return:
    """
    for nome in nomes:
        if nome not in listaNomes:
            with open("listaChamada.csv", 'a') as file:
                file.writelines(f'\n{nome}, - , - ,ausente')
            file.close()



def MarcarPresenca(nome):
    """
    Marca a presença e o horário de entrada do aluno no arquivo "listaChamada.csv", assim como horario de saida se já
    estiver presente na chamada
    :param nome: nome do aluno
    :return:
    """
    # carrega a chamada em obj pandas para editar
    chamadapd = pd.read_csv("listaChamada.csv")
    # acha o index do nome atual na lista, subtrai 1 por causa da linha inicial

    n = datetime.now().time()
    presenca = []

    with open('listaChamada.csv', 'a') as file:
        if nome not in listaNomes:

            presenca = [nome, 0]

            dtString = n.strftime('%H:%M:%S')
            # se a hora atual passar da entrada + atraso:
            if hr_atraso.time() < n < saida:
                file.writelines(f'\n{nome}, {dtString}, - , -')
                listaNomes.append(nome)
                presenca[1] += 1
            # se a hora atual passar da hora de saida:
            elif n >= saida:
                file.writelines(f'\n{nome}, - , - , -')
                listaNomes.append(nome)
                listaSaiu.append(nome)
            else:
                file.writelines(f'\n{nome}, {dtString}, - , -')
                listaNomes.append(nome)
                presenca[1] += 2
            nome_index = -1
            listaStatus.append(presenca)
        elif nome not in listaSaiu and n >= saida:
            dtString = n.strftime('%H:%M:%S')

            nome_index = listaNomes.index(nome) - 1
            presenca = [nome, listaStatus[nome_index][1]]

            # adiciona o hr de saida na coluna saida com pandas
            chamadapd.loc[nome_index, 'saida'] = dtString
            chamadapd.to_csv("listaChamada.csv", index=False)
            listaSaiu.append(nome)
            presenca[1] += 1

            # econtra a pessoa atual na listaStatus, para evitar duplicados
            for item in listaStatus:
                if nome in item[0]:
                    listaStatus[listaStatus.index(item)][1] = presenca[1]
                else:
                    listaStatus.append(presenca)
        file.close()
        AtualizarStatus(nome)


def findEncoding(images):
    """
    :param images:
    :return:
    """

    encodeList = []
    # converte todass as imagens da lista pra RGB
    for image in images:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encodeList.append(encode)
    return encodeList

#lista de todas as imagens conhecidas já convertidas
encodeListConhecido = findEncoding(images)


cam = cv2.VideoCapture(0)
count = 0
nomeAtt = ''
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# lista de todos os rostos que a camera detectar dentro do loop
rostos = []
while True:

    _, img = cam.read()
    # inverte a camera
    img = cv2.flip(img, 1)

    # diminui a imagem para 1/4 do tamanho pra agilizar o processo
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    # Desenha o retangulo no rosto
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    cv2.imshow('Webcam', img)
    cv2.waitKey(1)

    mtnome = utils.find_match(nomes, encodeListConhecido, imgS)
    rostos.append(mtnome)
    # se o mesmo rosto for identificado 5 vezes quebra o loop
    if rostos.count(mtnome) > 4 and mtnome is not None:
        break


index_aluno = listaNomes.index(mtnome)
# carrega a imagem de referencia do aluno atual
img_reconhecida = cv2.imread(f"imagensChamada/{mtnome}.jpg")
cv2.imshow('Confirmação', img_reconhecida)
cv2.waitKey(5000)
