
listaNomes = [] #nome dos alunos que já estão presentes, começa vazia
listaSaiu = [] # lista dos alunos que já sairam, começa vazia
listaStatus = [[nome, status]] # lista do status de cada aluno
presenca = [] # variavel temporario para guardar nome e status do aluno
nome = nome_do_aluno_atual

hr_entrada, hr_atraso, hr_saida = load_configs() #função que lê o aqrquivo de configurações e atribui os horarios
agora = datetime.now().time() # hora atual sem a data
if nome not in listaNomes: # se o nome do aluno ainda não esta na lista de presenças:

    if hr_atraso.time() < agora < hr_saida: # se o aluno chega depois do horario de atraso e antes da aula acabar recebe uma presença
        listaNomes.append(nome) #adciiona o aluno na lista de presença
        presenca[1] += 1

    elif agora >= saida:  # se a hora atual passar da hora de saida e o aluno não está na chamada recebe 0 presenças
        listaNomes.append(nome) #adciiona o aluno na lista de presença
        listaSaiu.append(nome)
    else: # se o aluno chega no horário certo recebe 2 presenças
        listaNomes.append(nome) #adciiona o aluno na lista de presença
        presenca[1] += 2
        listaStatus.append(presenca)
elif nome not in listaSaiu and agora >= saida: # se o aluno esta na lista de presenças, ainda não saiu e o horário de
                                                # saida já esta aberto, ganha mais 1 presença, para um maximo de 3
    presenca[1] += 1

# converter o numero de presenças para o status
if presenca[1] == 1:
    msg = 'presente(atraso)'
elif presenca[1] == 2:
    msg = 'presente(parcial)'
elif presenca[1] == 3:
    msg = 'presente'

