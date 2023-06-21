import cv2
import face_recognition
import numpy as np
from datetime import datetime, timedelta, date
import pandas as pd
import csv
from multiprocessing import pool
import mysql.connector
import os.path


def conectar_db():
    config = {
        'user': 'admin',
        'password': 'facerecon1234',
        'host': 'mysqlserver.cvhmu0h9hdef.us-east-2.rds.amazonaws.com',
        'database': 'facereconDB'
    }

    conn = mysql.connector.connect(**config)
    return conn

def remover_linhas_em_branco(nome_arquivo):
    linhas_removidas = 0
    linhas_totais = 0

    with open(nome_arquivo, 'r', newline='') as arquivo_csv:
        leitor = csv.reader(arquivo_csv)
        linhas = list(leitor)

    with open(nome_arquivo, 'w', newline='') as arquivo_csv:
        escritor = csv.writer(arquivo_csv)

        for linha in linhas:
            if linha:
                escritor.writerow(linha)
            else:
                linhas_removidas += 1

            linhas_totais += 1

    return linhas_removidas, linhas_totais


# cnx = conectar_db()
def find_match(name_list, encode_list, img):
    """
        Encontra o rosto atual na lista de chamada
    :param name_list: lista com todos os nomes da chamada
    :param encode_list: lista das fotos dos alunos convertidas em array
    :param img: frame atual da camera, de preferencia reduzir o tamanho para 1/4 do original
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
        # se o mesmo rosto for identificado 4 vezes quebra o loop
        return match


def load_configs():
    """
    Carrega as configurações de horário
    :return: retorna hora de entrada e saida em formato datetime, assim como a tolerancia em minutos
    """
    with open("configuracoes.txt", "r") as file:
        lines = [line.rstrip() for line in file]

        # pega só o valor numérico de cada linha
        entrada = lines[0].split()[2]
        saida = lines[1].split()[2]
        tolerancia = lines[2].split()[2]
        seguranca = lines[3].split()[2]
        senha = lines[4].split()[2]

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

            return dt_entrada, dt_saida, hr_atraso, seguranca, senha


def AtualizarStatus(nome, listaNomes, listaStatus, conexao):
    """
    atualiza o status do aluno
    :param nome:
    :param listaNomes:
    :param listaStatus:
    :return:
    """

    importar_tabela_db('chamada',conexao)

    pds = pd.read_csv("../listaChamada.csv")
    nome_index = listaNomes.index(nome) - 1
    status = listaStatus[nome_index]
    msg = 'ausente'
    if status[1] == 1:
        msg = 'presente(atraso)'
    elif status[1] == 2:
        msg = 'presente(parcial)'
    elif status[1] == 3:
        msg = 'presente'

    atualizar_presenca_db('chamada', conexao, nome)

    with open('../listaChamada.csv', 'a') as file:
        pds.loc[nome_index, 'status'] = msg
        pds.to_csv("../listaChamada.csv", index=False)
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
            with open("../listaChamada.csv", 'a') as file:
                file.writelines(f'\n{nome}, - , - ,ausente')
            file.close()
def findEncoding(images):
    """
    Cria os encodes de todas as fotos
    :param images:lista com as fotos de todos os alunos
    :return:
    """

    encodeList = []
    for image in images:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encodeList.append(encode)
    return encodeList


def create_encode_file(imagelist, file_name):

    encodelist = findEncoding(imagelist)

    if os.path.exists(f"../encode/{file_name}.csv"):
        pass
    else:
        open(f"../encodes/{file_name}.csv", 'x')
        with open(f"../encodes/{file_name}.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            for array in encodelist:
                writer.writerow(array)
            file.close()

def importar_tabela_db(tabela, conexao):
    query = f"SELECT * FROM `{tabela}`"
    cursor = conexao.cursor()
    cursor.execute(query)
    colunas_selecionadas = ['nome', 'entrada', 'saida', 'status']

    resultados = cursor.fetchall()

    colunas = [i[0] for i in cursor.description]
    df = pd.DataFrame(resultados, columns=colunas)

    df = df[colunas_selecionadas]
    df = df.replace('', '-')
    print(df)
    df.to_csv("../listaChamada.csv", index=False)

    cursor.close()


def MarcarPresenca(nome, listaNomes, listaSaiu, listaStatus, conexao):
    """
    Marca a presença e o horário de entrada do aluno no arquivo "listaChamada.csv", assim como horario de saida se já
    estiver presente na chamada
    :param nome: nome do aluno
    :return:
    """
    # carrega a chamada em obj pandas para editar
    chamadapd = pd.read_csv("../listaChamada.csv")
    # acha o index do nome atual na lista, subtrai 1 por causa da linha inicial

    importar_tabela_db('chamada', conexao)

    entrada, saida, hr_atraso, _, _ = load_configs()

    hr_atraso = hr_atraso.time()

    n = datetime.now().time()
    presenca = []

    with open('../listaChamada.csv', 'a') as file:
        if nome not in listaNomes and not None:

            presenca = [nome, 0]

            dtString = n.strftime('%H:%M:%S')
            # se a hora atual passar da entrada + atraso:
            if hr_atraso < n < saida:
                file.writelines(f'\n{nome}, {dtString}, - , -')
                listaNomes.append(nome)
                presenca[1] += 1

            # se a hora atual passar da hora de saida:
            elif n >= saida:
                file.writelines(f'\n{nome}, - , - , -')
                listaNomes.append(nome)
                listaSaiu.append(nome)
            elif hr_atraso > n > entrada:
                file.writelines(f'\n{nome}, {dtString}, - , -')
                listaNomes.append(nome)
                presenca[1] += 2
            nome_index = -1
            listaStatus.append(presenca)
            file.close()
            inserir_presenca_db('chamada', conexao, nome)
        elif nome not in listaSaiu and n >= saida:
            dtString = n.strftime('%H:%M:%S')

            nome_index = listaNomes.index(nome) - 1
            presenca = [nome, listaStatus[nome_index][0]] #carregar listaStatus

            # adiciona o hr de saida na coluna saida com pandas
            chamadapd.loc[nome_index, 'saida'] = dtString
            chamadapd.to_csv("../listaChamada.csv", index=False)
            listaSaiu.append(nome)
            presenca[1] += 1

            # econtra a pessoa atual na listaStatus, para evitar duplicados
            for item in listaStatus:
                if nome in item[0]:
                    listaStatus[listaStatus.index(item)][1] = presenca[1]
                else:
                    listaStatus.append(presenca)

            if len(listaNomes) > 1:
                AtualizarStatus(nome, listaNomes, listaStatus, conexao)


def ler_chamada():
    """
    le o arquivo de chamada e organiza as informações em listas
    :return:
    """

    with open('..\listaChamada.csv', 'r') as f:
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
    return listaStatus, listaNomes, listaSaiu


def inserir_presenca_db(tabela, conexao, aluno):
    """
    Insere os dados de um aluno na lista de chamada do banco

    :param tabela: nome da tabela dentro do banco de dados
    :param conexao: objeto de conexão com o banco
    :param aluno: nome do aluno a ser adicionado
    :return:
    """
    conn = conexao
    cursor = conn.cursor(buffered=True)

    remover_linhas_em_branco('../listaChamada.csv')

    with open('../listaChamada.csv', 'r') as csv_file:
        # Criar um leitor de CSV
        csv_reader = csv.reader(csv_file)
        data = date.today()
        hoje = data.strftime("%d/%m/%Y")

        # Ignorar o cabeçalho do CSV
        next(csv_reader)

        # acha o nome do aluno no csv e insere na tabela
        for linha in csv_reader:
            if linha[0] == aluno:
                nome = linha[0]
                hr_entrada = linha[1]
                saida = linha[2]
                status = linha[3]

                query = f"INSERT INTO `{tabela}` (nome, entrada, saida, status, data) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (nome, hr_entrada, saida, status, hoje))

        # Confirmar as alterações
        conn.commit()
        importar_tabela_db('chamada', conexao)
    csv_file.close()
def atualizar_presenca_db(tabela, conexao, aluno):

    conn = conexao
    cursor = conn.cursor(buffered=True)
    data = date.today()
    hoje = data.strftime("%d/%m/%Y")
    remover_linhas_em_branco('listaChamada.csv')
    with open('listaChamada.csv', 'r') as csv_file:
        # Criar um leitor de CSV
        csv_reader = csv.reader(csv_file)

        # Ignorar o cabeçalho do CSV
        next(csv_reader)

        # acha o nome do aluno no csv e insere na tabela
        for linha in csv_reader:
            if linha[0] == aluno:
                nome = linha[0]
                hr_entrada = linha[1]
                saida = linha[2]
                status = linha[3]

                query = f"UPDATE `{tabela}` SET nome = %s, entrada = %s, saida = %s, status = %s, data = %s WHERE nome = %s"
                cursor.execute(query, (nome, hr_entrada, saida, status, hoje, nome))

        # Confirmar as alterações
        conn.commit()
        atualizar_presenca_db('chamada', conexao, aluno)
        importar_tabela_db('chamada', conexao)
    csv_file.close()




def abrir_chamada(tabela_fonte, tabela_destino, conexao):

    cursor_fonte = conexao.cursor(buffered=True)
    cursor_destino = conexao.cursor(buffered=True)

    query = f"SELECT * FROM `{tabela_fonte}`"
    cursor_fonte.execute(query)

    for linha in cursor_fonte.fetchall():
        cursor_destino.execute(f"INSERT INTO {tabela_destino}(nome) VALUES(%s)", (linha[1],))

    cursor_fonte.close()
    cursor_destino.close()
    conexao.commit()










