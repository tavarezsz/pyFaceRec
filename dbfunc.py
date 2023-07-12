import mysql.connector
import base64
from cryptography.fernet import Fernet
import os



chave = b'D2UfMEE158hqPSVVrkGTql59yfIolwjwcC0tvL8FxeM='

def criptografar_dados(dados):
    f = Fernet(chave)
    return f.encrypt(dados)

def descriptografar_dados(dados_criptografados):
    f = Fernet(chave)
    return f.decrypt(dados_criptografados)


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

    imagem_criptografada = criptografar_dados(imagem_binaria)
    imagem_base64 = base64.b64encode(imagem_criptografada)

    try:
        # Criar um cursor para executar as consultas SQL
        cursor = conexao.cursor()


        # Inserir a imagem no banco de dados
        consulta = f"UPDATE turma01 SET foto = %s WHERE nome = '{nome}'"
        dados = (imagem_base64.decode(),)
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
            imagem_base64 = resultado[1]

            imagem_criptografada = base64.b64decode(imagem_base64)
            imagem_descriptografada = descriptografar_dados(imagem_criptografada)

            # Salvar a imagem no diretório de destino
            caminho_imagem = os.path.join(diretorio_destino, f"{nome}.jpg")
            with open(caminho_imagem, 'wb') as arquivo_imagem:
                arquivo_imagem.write(imagem_descriptografada)

        print("Imagens salvas com sucesso!")



    except mysql.connector.Error as erro:
        print(f"Erro ao buscar as imagens: {erro}")

    finally:
        resultados = cursor.fetchall()
        # Fechar o cursor e a conexão com o banco de dados
        cursor.close()
        conexao.close()

