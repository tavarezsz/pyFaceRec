import mysql.connector
import pandas as pd
import datetime
import base64
from PIL import Image
import io
import os

'''
config = {
  'user': 'admin',
  'password': 'facerecon1234',
  'host': 'mysqlserver.cvhmu0h9hdef.us-east-2.rds.amazonaws.com',
  'database': 'facereconDB'
}

conn = mysql.connector.connect(**config)

cursor = conn.cursor(buffered=True)

cursor.execute("SELECT * FROM `turma01`")

resultados = cursor.fetchall()

# Iterando sobre os resultados
for linha in resultados:
    img = linha[2]
    binary_data = base64.b64decode(img)

    # Convert the bytes into a PIL image
    image = Image.open(io.BytesIO(binary_data))

    # Display the image
    image.show()
    print(img)
'''
import mysql.connector

import mysql.connector

def inserir_imagem(caminho_imagem,nome):
    # Estabelecer conexão com o banco de dados
    conexao = mysql.connector.connect(
        host='mysqlserver.cvhmu0h9hdef.us-east-2.rds.amazonaws.com',
        user='admin',
        password='facerecon1234',
        database='facereconDB'
    )

    # Abrir o arquivo de imagem em modo binário
    with open(caminho_imagem, 'rb') as arquivo_imagem:
        imagem_binaria = arquivo_imagem.read()


    try:
        # Criar um cursor para executar as consultas SQL
        cursor = conexao.cursor()


        # Inserir a imagem no banco de dados
        consulta = f"UPDATE turma01 SET foto = %s WHERE nome = '{nome}'"
        dados = (imagem_binaria,)
        cursor.execute(consulta, dados)

        # Confirmar as alterações
        conexao.commit()

        print("Imagem inserida com sucesso!")

    except mysql.connector.Error as erro:
        print(f"Erro ao inserir a imagem: {erro}")

    finally:
        # Fechar o cursor e a conexão com o banco de dados
        cursor.close()
        conexao.close()

def buscar_imagens(diretorio_destino, tabela):
    # Estabelecer conexão com o banco de dados
    conexao = mysql.connector.connect(
        host='mysqlserver.cvhmu0h9hdef.us-east-2.rds.amazonaws.com',
        user='admin',
        password='facerecon1234',
        database='facereconDB'
    )

    try:
        # Criar um cursor para executar as consultas SQL
        cursor = conexao.cursor()

        # Selecionar as imagens da tabela
        consulta = f"SELECT nome, foto FROM {tabela}"
        cursor.execute(consulta)

        # Verificar se o diretório de destino existe, caso contrário, criá-lo
        if not os.path.exists(diretorio_destino):
            os.makedirs(diretorio_destino)

        # Percorrer os resultados da consulta
        for indice, resultado in enumerate(cursor):
            nome = resultado[0]
            imagem_binaria = resultado[1]

            # Salvar a imagem no diretório de destino
            caminho_imagem = os.path.join(diretorio_destino, f"{nome}.jpg")
            with open(caminho_imagem, 'wb') as arquivo_imagem:
                arquivo_imagem.write(imagem_binaria)

        print("Imagens salvas com sucesso!")



    except mysql.connector.Error as erro:
        print(f"Erro ao buscar as imagens: {erro}")

    finally:
        resultados = cursor.fetchall()
        # Fechar o cursor e a conexão com o banco de dados
        cursor.close()
        conexao.close()


def inserir(entrada, nome_db):
    chamadapd = pd.read_csv("listaChamada.csv")
    nome = entrada[0]
    hr_entrada = entrada[1]
    saida = entrada[2]
    status = entrada[3]
    data =entrada[4]
    query = "INSERT INTO `chamada` (nome, entrada, saida, status, data) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (nome, hr_entrada, saida, status, data))
    conn.commit()



'''for i in range(10):
    nome = input('nome:')
    hj = datetime.date.today()
    date = hj.strftime("%d/%m/%Y")
    teste = [f'{nome}', '19:14:00', '22:09:45', 'presente', date]
    inserir(teste, 'chamada')
    print(nome)'''

'''results = cursor.fetchall()
    
for row in results:
    print(row)'''

#gerar_chave()

#inserir_imagem('imagensChamada\\joao.jpg', 'joão')
#buscar_imagens('imagensturma03', 'turma01')/


'''cursor.close()
conn.close()
'''