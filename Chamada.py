import cv2
import numpy as np
import face_recognition
import os
import pandas as pd
from datetime import datetime, timedelta
import mysql.connector
from flask import Flask, jsonify, request

path = 'imagensChamada'
images = []
nomes = []
lista = os.listdir(path)
listaStatus = []

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


def desenhar_rosto(frame, local):
    """
    :param frame: frame atual da camera
    :param local: coordenadas do rosto
    :return:
    """

    top, right, bottom, left = local
    top, right, bottom, left = top*2, right*2, bottom*2, left*2

    cor = (204, 204, 0)

    cv2.rectangle(frame, (left, top), (right, bottom), cor, 2)
    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), cor, cv2.FILLED)
    cv2.putText(img, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)


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

            # econtra a pessoa atula na listaStatus, para evitar duplicados
            for item in listaStatus:
                if name in item[0]:
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
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

#lista de todas as imagens conhecidas já convertidas
encodeListConhecido = findEncoding(images)


cam = cv2.VideoCapture(0)
count = 0
nomeAtt = ''
while count < 1000:

    sucesso, img = cam.read()
    # inverte a camera
    img = cv2.flip(img, 1)
    # diminui o tamanho da imagem para agilizar
    imgS = cv2.resize(img, (0, 0), None, 0.5, 0.5)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesFrameAtt = face_recognition.face_locations(imgS)
    encodesFrameAtt = face_recognition.face_encodings(imgS, facesFrameAtt)

    for encodeFace, faceLoc in zip(encodesFrameAtt, facesFrameAtt):
        matches = face_recognition.compare_faces(encodeListConhecido, encodeFace)
        faceDis = face_recognition.face_distance(encodeListConhecido, encodeFace)
        print(faceDis)
        matchIndex = np.argmin(faceDis)

        # Desenha o retangulo no rosto se o rosto bater com algum da lista
        if matches[matchIndex]:
            name = nomes[matchIndex].upper()
            nomeAtt = nomes[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            desenhar_rosto(img, faceLoc)
            MarcarPresenca(name)
            count += 1
            

    cv2.imshow('Webcam', img)
    cv2.waitKey(1)

print(nomeAtt)
#teste = cv2.imread('imagensChamada/eduardo.jpg')
#testeS = cv2.resize(teste, (0, 0), None, 0.5, 0.5)

#cv2.imshow('image', testeS)
