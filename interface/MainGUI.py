import time
import cProfile, pstats
from tkinter import messagebox
import tkinter
from datetime import datetime, timedelta
import cv2
import face_recognition
from PIL import Image, ImageTk, ImageDraw
import customtkinter as ck
from utils import *
from time import sleep
import os
from testeDB import buscar_imagens

ck.set_appearance_mode("Dark")
ck.set_default_color_theme("blue")

class MainPage:
    def __init__(self, master):
        self.master = master
        self.senha = 'root'

        master.geometry('400x300')
        self.label = ck.CTkLabel(master, text="FaceRecon", font=('Arial', 20))
        self.label.pack(padx=20, pady=25)

        self.cbTurmas = ck.CTkComboBox(master, values=self.ler_turmas(), state='readonly')
        self.cbTurmas.pack()
        self.cbTurmas.set("Selecione a turma")

        self.btnIniciar = ck.CTkButton(master, text="Iniciar", font=('Arial', 16), command=self.openIniciar)
        self.btnIniciar.pack(padx=20, pady=25)

        self.btnConfiguracoes = ck.CTkButton(master, text="Configurações", font=('Arial', 16), command=self.openConfigs)
        self.btnConfiguracoes.pack(padx=20, pady=0)

        self.btnCarregarTurma = ck.CTkButton(master, text="Carregar nova turma", font=('Arial', 16), command=self.carregar_turma)
        self.btnCarregarTurma.pack(pady=20)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def message(self):
        window = ck.CTkToplevel(self.master)
        window.title('Bem-vindo Eduardo!!!')
        window.grab_set()
        window.after(3000, lambda: window.destroy())


    def ler_turmas(self):
        """
        le o nome dos arquivos da pasta encodes e coloca como opções do combo box
        :return: retorna lista com os nomes dos arquivos
        """
        turmas = [os.path.splitext(f)[0] for f in os.listdir("../encodes")]

        return turmas


    def carregar_turma(self):

        turmas = self.ler_turmas()
        dialog_turma = ck.CTkInputDialog(text="Insira o nome da turma",
                                        title="Atenção")
        #turma = dialog_turma.get_input()
        turma = 'hentor'
        input_turma = dialog_turma.get_input()

        if turma in turmas:
           warning = messagebox.showwarning('Aviso', f"A turma {turma} já esta cadastrada, deseja subscreve-la?")
           if warning:
               dialog_turma = ck.CTkInputDialog(text="Insira o nome da turma(deve estar cadastrada no banco)", title="Atenção")
               input_turma = dialog_turma.get_input()
               if os.path.exists(f'../imagens{turma}'):
                   pass
                   #create_encode_file(turma)
                    #read_image_lista(turma)
        else:

           dialog_tabela = ck.CTkInputDialog(text="Insira o nome da turma em banco(precisa estar cadastrado)",
                                            title="Atenção")
           tabela = dialog_tabela.get_input()
           buscar_imagens(f'../imagens{input_turma}', tabela)
           imagens = ler_lista_imagens(f'../imagens{input_turma}')
           dialog_nome = ck.CTkInputDialog(text="Digite um nome para o cadastro da turma no app",
                                            title="Atenção")
           input_nome = dialog_nome.get_input()
           create_encode_file(imagens, input_nome.lower())

           messagebox.showinfo('Sucesso')
           self.cbTurmas.configure(values=self.ler_turmas())



    def popupSenha(self):

        while True:

            sucesso = False

            dialog_senha = ck.CTkInputDialog(text="Insira a senha de segurança:", title="Atenção")
            input_senha = dialog_senha.get_input()

            if not input_senha:
                dialog_senha.destroy()
                break
            elif input_senha.strip() != self.senha.strip():
                messagebox.showwarning("Aviso", "Senha Incorreta")
            else:
                sucesso = True
                break
        return sucesso

    def openConfigs(self):
        self.newWindow = ck.CTkToplevel(self.master)
        self.app = PagCofigs(self.newWindow)
        self.newWindow.grab_set()

    def openIniciar(self):
        global turma_selecionada

        turma_selecionada = self.cbTurmas.get()
        if turma_selecionada == 'Selecione a turma':
            warning = messagebox.showwarning('Aviso', 'Selecione uma turma!')
        else:
            self.iniciar = ck.CTkToplevel(self.master)

            self.app2 = PagIniciar(self.iniciar)
            self.iniciar.grab_set()

    def show_message(self):
        pass

    def on_closing(self):
        if messagebox.askyesno(title="Sair?", message="Tem certeza que deseja sair?"):
            self.master.destroy()


class PagCofigs:
    def __init__(self, master):
        self.seguranca = tkinter.IntVar()
        self.master = master

        fonte = 'Arial'
        master.title("Configurações")
        master.geometry("600x350")
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.lblTitulo = ck.CTkLabel(master, font=(fonte, 20), text='Configurações')
        self.lblTitulo.pack()

        self.lblEntrada = ck.CTkLabel(master, font=('Arial', 16), text='Horario de entrada:', padx=5)
        self.lblEntrada.place(x=5, y=45)

        self.txtEntrada = ck.CTkTextbox(master, width=100, height=10, fg_color='grey')
        self.txtEntrada.place(x=150, y=45)

        self.lblEntradaDisc = ck.CTkLabel(master, font=('Arial', 12), text='Define a partir de que horário o sistema '
                                                                           'começa\na contabilizar a '
                                                                           'entrada do aluno', pady=10)
        self.lblEntradaDisc.place(x=5, y=75)

        self.lblSaida = ck.CTkLabel(master, font=('Arial', 16), text='Horario de saída:', padx=5)
        self.lblSaida.place(x=300, y=45)

        self.txtSaida = ck.CTkTextbox(master, width=100, height=10, fg_color='grey')
        self.txtSaida.place(x=430, y=45)

        self.lblSaidaDisc = ck.CTkLabel(master, font=('Arial', 12),
                                        text='Define a partir de que horário o sistema começa\n'
                                             'a contabilizar a saída do aluno', pady=10)
        self.lblSaidaDisc.place(x=300, y=75)

        self.lblTolerancia = ck.CTkLabel(master, font=('Arial', 16), text='Tolerancia de Entrada:', padx=5)
        self.lblTolerancia.place(x=5, y=165)

        self.txtTolerancia = ck.CTkTextbox(master, width=100, height=10, fg_color='grey')
        self.txtTolerancia.place(x=175, y=165)

        self.lblToleranciaDisc = ck.CTkLabel(master, font=('Arial', 12),
                                             text='Define até quantos minutos após o horário de '
                                                  'entrada\n o aluno pode chegar sem receber '
                                                  'atraso', pady=10)
        self.lblToleranciaDisc.place(x=5, y=200)

        self.rdSeguranca = ck.CTkCheckBox(master, font=('Arial', 16), text='Modo de segurança', variable=self.seguranca)
        self.rdSeguranca.place(x=300, y=165)

        self.lblSeguranca = ck.CTkLabel(master, font=('Arial', 12), text='Quando ativo requer uma senha para alterar\n'
                                                                         'configurações, assim como iniciar e parar o '
                                                                         'programa')
        self.lblSeguranca.place(x=300, y=207)

        self.btnSenha = ck.CTkButton(master, font=(fonte, 12), text='Alterar senha', width=50, height=10,
                                     command=self.mudar_senha)
        self.btnSenha.place(x=300, y=247)

        self.btnAplicar = ck.CTkButton(master, font=(fonte, 16), text='Aplicar', command=self.get_data)
        self.btnAplicar.place(x=450, y=300)

        self.senha = self.read_data()

        self.read_data()

    def mudar_senha(self):

        while True:
            dialog = ck.CTkInputDialog(text="Insira a senha de administrador para mudar sua senha", title="Mudar Senha")
            dialog_value = dialog.get_input()

            if not dialog_value:
                dialog_value.destroy()
                break
            elif dialog_value.strip() != self.senha.strip():
                messagebox.showwarning("Aviso", "Senha Incorreta, contate seu administrador")
            else:
                dialog_novo = ck.CTkInputDialog(text="Insira a nova senha", title="Mudar Senha")
                nova_senha = dialog_novo.get_input()

                with open('configuracoes.txt', 'r') as file:
                    data = file.readlines()

                data[4] = f"senha = {nova_senha}\n"

                with open('configuracoes.txt', 'w', encoding='utf-8') as file:
                    file.writelines(data)
                break

    def get_data(self):
        """
        Converte as strings de tempo em datetime e salva no arquivo "configuracoes.txt"

        :return:
        """
        teste = self.popupSenha()

        if teste:

            hr_entrada = self.txtEntrada.get("1.0", "end").strip()
            hr_saida = self.txtSaida.get("1.0", "end").strip()
            tolerancia = self.txtTolerancia.get("1.0", "end").strip()

            try:
                tolerancia = int(tolerancia)
            except ValueError:
                print('Digite valores válidos')
            else:
                if 60 >= tolerancia >= 0:
                    try:
                        hr_entrada = datetime.strptime(hr_entrada, "%H:%M:%S").time()
                        hr_saida = datetime.strptime(hr_saida, "%H:%M:%S").time()
                    except ValueError:
                        print("[ERRO] Digite valores no formato HH:MM:SS")

                    else:
                        print(hr_entrada)
                        with open("configuracoes.txt", "w") as file:
                            file.write(f"hora_entrada = {hr_entrada}\nhora_saida = {hr_saida}\ntolerancia = "
                                       f"{tolerancia}\nmodo_de_seguranca = {self.seguranca.get()}")
                            file.close()
                else:
                    print("A tolerancia não pode ser maior que 60 minutos ou menor que zero")
        else:
            pass

    def popupSenha(self):

        while True:

            sucesso = False

            dialog_senha = ck.CTkInputDialog(text="Insira a senha de segurança:", title="Atenção")
            input_senha = dialog_senha.get_input()

            if not input_senha:
                dialog_senha.destroy()
                break
            elif input_senha.strip() != self.senha.strip():
                messagebox.showwarning("Aviso", "Senha Incorreta")
            else:
                sucesso = True
                break
        return sucesso

    def read_data(self):
        """
        Lê o arquivo de configurações e exibe em cada textbox a sua configuração

        :return:
        """
        with open("configuracoes.txt", 'r') as file:
            lines = [line.rstrip() for line in file]

            #limpa os campos
            self.txtEntrada.delete("1.0", 'end')
            self.txtSaida.delete("1.0", 'end')
            self.txtTolerancia.delete("1.0", 'end')

            # pega só o horario da linha 1
            entrada = lines[0].split()[2]
            self.txtEntrada.insert("1.0", entrada)
            saida = lines[1].split()[2]
            self.txtSaida.insert("1.0", saida)
            tolerancia = lines[2].split()[2]
            self.txtTolerancia.insert("1.0", tolerancia)
            seguranca = int(lines[3].split()[2])
            if seguranca == 1:
                self.rdSeguranca.select()
        return senha_geral

    def on_closing(self):
        if messagebox.askyesno(title="Sair?", message="Tem certeza que deseja sair?"):
            self.master.destroy()


class PagIniciar:
    def __init__(self, master):
        self.master = master
        master.title("FaceRecon")
        master.geometry("800x500")

        self.nomes, self.encodelistConhecido = load_encodes('../imagensChamada', 'turma01.csv')

        # bind esq para sair
        master.bind('<Escape>', lambda e: master.quit())

        # Create a label and display it on app
        self.label = ck.CTkLabel(master, text='')
        self.label.pack()
        self.lbl_camera = tkinter.Label(master, text='')
        self.lbl_camera.pack()
        self.btn_iniciar = ck.CTkButton(master, text="Iniciar", command=lambda: self.open_camera(stop=False))
        self.btn_iniciar.pack()
        self.btn_parar = ck.CTkButton(master, text='Parar', command=lambda: self.open_camera(stop=True))
        self.btn_parar.pack()
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        self.vid = cv2.VideoCapture(0)
        #importar_tabela_db('chamada', conexao)

        self.pessoas = []
        # variavel para performance
        self.process_this = True
        self.count = 0
        self.nomes_chegaram = []
        print(turma_selecionada)
        if turma_selecionada == 'turma01':
            self.turma = 'chamada'
        else:
            self.turma = 'chamada02'

    def message(self, msg):
        window = ck.CTkToplevel(self.master)
        window.title('Confirmação')
        window.geometry("300x100")
        lbl = ck.CTkLabel(window, text=msg)
        lbl.pack()
        window.grab_set()
        window.after(2000, lambda: window.destroy())


    def open_camera(self, stop=False):

        now = datetime.now().time()

        lStatus, lNomes, lSaiu = ler_chamada()

        # converte o último frame em imagem
        cv2image = cv2.cvtColor(self.vid.read()[1], cv2.COLOR_BGR2RGB)
        cv2image = cv2.flip(cv2image, 1)
        cv2image = cv2.resize(cv2image,(0,0), None, 1.5, 1.5)
        gray = cv2.cvtColor(cv2image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        # diminui a imagem para 1/4 para agilizar o processo
        imgS = cv2.resize(cv2image, (0, 0), None, 0.25, 0.25)

        for (x, y, w, h) in faces:
            cv2.rectangle(cv2image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        img = Image.fromarray(cv2image)
        # conversão de imagem
        imgtk = ImageTk.PhotoImage(image=img)
        self.lbl_camera.imgtk = imgtk
        self.lbl_camera.configure(image=imgtk)

        # tenta encontrar o rosto atual na lista de encodes da chamada
        mtnome = None

        #processa a imagem a cada 5 frames para otimizar performance
        if self.count % 5 == 0:
            pass
            mtnome = find_match(self.nomes, self.encodelistConhecido, imgS)
            print(mtnome)
        else:
            mtnome = None

        if mtnome != 'desconhecido' and not None:
            self.pessoas.append(mtnome)

        if self.pessoas.count(mtnome) > 1 and mtnome != 'desconhecido' and mtnome is not None:
            # atualiza a presença quando o aluno não está na chamada
            if mtnome not in self.nomes_chegaram and now > hr_entrada:
                '''img_reconhecida = cv2.imread(f"../imagensChamada/{mtnome}.jpg")
                img_reconhecida = cv2.cvtColor(img_reconhecida, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img_reconhecida)
                imgt = ImageTk.PhotoImage(image=img)
                self.lbl_camera.imgt = imgt
                self.lbl_camera.configure(image=imgt)
                self.lbl_camera.after_idle(time.sleep, 2)'''
                self.label.configure(text=f'Último Aluno: {mtnome}')
                MarcarPresenca(mtnome, conexao, self.turma)
                self.message(f'Bem-Vindo {mtnome}')


                # após identificar uma pessoa com sucesso reinicia a lista de rostos
                self.pessoas.clear()
                self.nomes_chegaram.append(mtnome)


            # atualiza a presença quando passou do horario de saida e o aluno ainda não saiu
            elif now > hr_saida and mtnome not in lSaiu and mtnome is not None:
                MarcarPresenca(mtnome, conexao, 'chamada')
                # carrega a foto de perfil do aluno
                img_reconhecida = cv2.imread(f"../imagensChamada/{mtnome}.jpg")
                img_reconhecida = cv2.cvtColor(img_reconhecida, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img_reconhecida)
                imgt = ImageTk.PhotoImage(image=img)
                self.lbl_camera.imgt = imgt
                self.lbl_camera.configure(image=imgt)
                # após identificar uma pessoa com sucesso reinicia a lista de rostos
                self.pessoas.clear()

        self.count += 1

        if stop is not True:
            self.tk_after = self.master.after(1, lambda: self.open_camera(stop=False))
        else:
            self.master.after_cancel(self.tk_after)
            self.btn_iniciar.configure(text='Retomar', command=lambda: self.open_camera(stop=False))


def ler_lista_imagens(path):
    images = []
    lista = os.listdir(path)

    # ler cada imagem da lista
    for im in lista:
        imgAtual = cv2.imread(f'{path}/{im}')
        images.append(imgAtual)
    return images



def load_encodes(path, file_name):
    images = []
    nomes = []
    lista = os.listdir(path)

    # ler cada imagem da lista
    for im in lista:
        imgAtual = cv2.imread(f'{path}/{im}')
        images.append(imgAtual)
        # adiciona o nome da imagem sem o .jpeg
        nomes.append(os.path.splitext(im)[0])
    # cria uma lista de encodes das imagens da chamada
    encodelistConhecido = []
    with open(f"../encodes/{file_name}", 'r') as file:
        reader = csv.reader(file)
        for linha in reader:
            linha = np.array(linha)
            linhanp = linha.astype(float)
            encodelistConhecido.append(linhanp)
    return nomes,  encodelistConhecido



with cProfile.Profile() as profile:

    listaStatus, listaNomes, listaSaiu = ler_chamada()

    hr_entrada, hr_saida, hr_atraso, seguranca, senha_geral = load_configs()

    conexao = conectar_db()

    root = ck.CTk()
    app = MainPage(root)
    root.mainloop()
''' results = pstats.Stats(profile)
results.sort_stats(pstats.SortKey.TIME)
results.print_stats()
'''
