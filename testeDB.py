import mysql.connector
import pandas as pd
import datetime
import base64
from PIL import Image
import io

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

cursor.close()
conn.close()
