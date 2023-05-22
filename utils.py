import cv2
import face_recognition
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
def find_match(name_list, encode_list, img):
    """
        Encontra o rosto atual na lista de chamada
    :param name_list: lista com todos os nomes da chamada
    :param encode_list: lista das fotos dos alunos convertidas em array
    :param img: frame atual da camera
    :return: retorna o nome do aluno no frame atual
    """
    match = 'desconhecido'

    facesFrameAtt = face_recognition.face_locations(img)
    encodesFrameAtt = face_recognition.face_encodings(img, facesFrameAtt)

    for encodeFace, faceLoc in zip(encodesFrameAtt, facesFrameAtt):
        matches = face_recognition.compare_faces(encode_list, encodeFace)
        faceDis = face_recognition.face_distance(encode_list, encodeFace)
        print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            match = name_list[matchIndex].upper()

        return match


def load_configs():
    """
    Carrega as configurações de horário
    :return: retorna hora de entrada e saida em formato datetime, assim como a tolerancia em minutos
    """
    with open("interface/configuracoes.txt", "r") as file:
        lines = [line.rstrip() for line in file]

        # pega só o valor numérico de cada linha
        entrada = lines[0].split()[2]
        saida = lines[1].split()[2]
        tolerancia = lines[2].split()[2]

        try:
            dt_entrada = datetime.strptime(entrada, "%H:%M:%S")
            dt_saida = datetime.strptime(saida, "%H:%M:%S")
            tolerancia = int(tolerancia)
        except ValueError:
            print("[ERRO]valores de configuração fora do formato HH/MM/SS")
        else:
            # adiciona os minutos de tolerancia ao horario de entrada
            hr_atraso = dt_entrada + timedelta(minutes=tolerancia)
            # pega apenas o horario
            dt_entrada = dt_entrada.time()
            dt_saida = dt_saida.time()

            return dt_entrada, dt_saida, hr_atraso


def AtualizarStatus(nome, listaNomes, listaStatus):
    """
    atualiza o status do aluno
    :param nome:
    :param listaNomes:
    :param listaStatus:
    :return:
    """

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

def fecharChamada(listaNomes, alunos):
    """
    Adicona os alunos que não fizeram a chamada como ausentes
    :param alunos: lista de todos os alunos na turma
    :param listaNomes: lista com os nomes dos alunos que já estão na chamada atual
    :return:
    """
    for nome in alunos:
        if nome not in listaNomes:
            with open("listaChamada.csv", 'a') as file:
                file.writelines(f'\n{nome}, - , - ,ausente')
            file.close()
def findEncoding(images):
    """
    Cria os encodes de todas as fotos
    :param images:lista com as fotos de todos os alunos
    :return:
    """

    encodeList = []
    # converte todass as imagens da lista pra RGB
    for image in images:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encodeList.append(encode)
    return encodeList

def MarcarPresenca(nome, listaNomes, listaSaiu, listaStatus):
    """
    PS: ainda tenho q fazer uns ajustes aqui!
    Marca a presença e o horário de entrada do aluno no arquivo "listaChamada.csv", assim como horario de saida se já
    estiver presente na chamada
    :param nome: nome do aluno
    :return:
    """
    # carrega a chamada em obj pandas para editar
    chamadapd = pd.read_csv("listaChamada.csv")
    # acha o index do nome atual na lista, subtrai 1 por causa da linha inicial

    entrada, saida, hr_atraso = load_configs()

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
        AtualizarStatus(nome, listaNomes, listaStatus)
