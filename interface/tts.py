import base64
import csv
from datetime import date
from utils import *

import mysql.connector

def atualizar_presenca_db(tabela, conexao, aluno):

    cursor = conexao.cursor(buffered=True)
    data = date.today()
    hoje = data.strftime("%d/%m/%Y")
    with open('../listaChamada.csv', 'r') as csv_file:
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
    csv_file.close()

def inserir_imagem(nome_tabela, nome_coluna, id_registro, caminho_imagem):
    # Configuração da conexão com o banco de dados
    cnx = mysql.connector.connect(
        user='admin',
        password='facerecon1234',
        host='mysqlserver.cvhmu0h9hdef.us-east-2.rds.amazonaws.com',
        database='facereconDB'
    )

    try:
        # Abre o arquivo da imagem em modo binário
        with open(caminho_imagem, 'rb') as arquivo_imagem:
            imagem = arquivo_imagem.read()
            imagem = base64.b64encode(imagem)

            # Prepara o comando SQL para inserir a imagem
            cursor = cnx.cursor(buffered=True)
            comando_sql = f"INSERT INTO {nome_tabela} (nome, {nome_coluna}) VALUES (%s, %s)"
            dados = ('Leandro_Amaral', imagem)

            # Executa o comando SQL
            cursor.execute(comando_sql, dados)
            cnx.commit()
            print("Imagem inserida com sucesso!")

    except mysql.connector.Error as erro:
        print(f"Erro ao inserir a imagem: {erro}")

    finally:
        # Fecha a conexão com o banco de dados
        cursor.close()
        cnx.close()

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
    csv_file.close()


# Exemplo de uso

conn = mysql.connector.connect(
    user='admin',
    password='facerecon1234',
    host='mysqlserver.cvhmu0h9hdef.us-east-2.rds.amazonaws.com',
    database='facereconDB'
)

# inserir_presenca_db('chamada', conn, 'EDUARDO')

# inserir_imagem('turma01', 'foto', 1, r'C:\Users\Eduardo T\Desktop\fotos\leandro.jpeg')

# atualizar_presenca_db('chamada', conn, 'EDUARDO')
'''path = '..\imagensChamada'
images = []
nomes = []
lista = os.listdir(path)
for im in lista:
    imgAtual = cv2.imread(f'{path}/{im}')
    images.append(imgAtual)

create_encode_file(images, 'turma02')
'''

remover_linhas_em_branco('../listaChamada.csv')
