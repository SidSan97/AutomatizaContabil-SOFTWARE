import tkinter as tk
from tkinter import *
from tkinter import filedialog, messagebox
from datetime import datetime
import shutil
import subprocess
import os
import requests
from tkinterdnd2 import TkinterDnD, DND_FILES
import json
import tempfile

idUser = 0
logado = False
arquivosUpload = None

def drop(event):
    global arquivosUpload

    # Obter o caminho dos arquivos arrastados
    caminhos_arquivos = event.data.split()  # Dividir a string para obter a lista de arquivos

    if caminhos_arquivos:
        label.config(text=f"Arquivo selecionado: {caminhos_arquivos}")
    
    arquivos = [caminho for caminho in caminhos_arquivos]
    
    # Verificar se todos os arquivos são PDFs
    for caminho_arquivo in arquivos:
        extensao = os.path.splitext(caminho_arquivo)[1]
        if extensao.lower() != ".pdf":
            messagebox.showerror("Erro", "Por favor, selecione apenas arquivos PDF.")
            return
    
    arquivosUpload = caminhos_arquivos

def selecionar_arquivo():
    caminhos_arquivos = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    if caminhos_arquivos:
        label.config(text=f"Arquivo selecionado: {caminhos_arquivos}")
        return caminhos_arquivos
    else:
        label.config(text="Nenhum arquivo selecionado")
        return None
    
def selecionarPdf():
    global arquivosUpload

    caminhos_arquivos = selecionar_arquivo()
    if not caminhos_arquivos:
        return
    
    arquivosUpload = caminhos_arquivos

def criarDiretorios(caminhos_arquivos, departamento):
    label.config(text="Enviando arquivos. Aguarde...")

    # Determinar o diretório onde o script Python está localizado
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))

    # Criar uma pasta específica dentro do diretório atual
    pasta_cliente = os.path.join(diretorio_atual, "CLIENTE")
    if not os.path.exists(pasta_cliente):
        os.makedirs(pasta_cliente)

    # Dentro da pasta CLIENTE, criar a pasta "fiscal" se não existir
    pasta_departamento = os.path.join(pasta_cliente, departamento)
    if not os.path.exists(pasta_departamento):
        os.makedirs(pasta_departamento)

    # Determinar o ano corrente
    ano_corrente = datetime.now().year
    pasta_ano = os.path.join(pasta_departamento, str(ano_corrente))
    if not os.path.exists(pasta_ano):
        os.makedirs(pasta_ano)

    # Determinar o mês corrente
    mes_corrente = datetime.now().month
    pasta_mes = os.path.join(pasta_ano, str(mes_corrente))
    if not os.path.exists(pasta_mes):
        os.makedirs(pasta_mes)

    for caminho_arquivo in caminhos_arquivos:
        # Caminho do arquivo de destino na pasta mes
        nome_arquivo = os.path.basename(caminho_arquivo)
        caminho_destino = os.path.join(pasta_mes, nome_arquivo)

        try:
            shutil.copy(caminho_arquivo, caminho_destino)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o arquivo: {e}")

    try:
        enviarPDF(caminhos_arquivos)
    finally:
        label.config(text='')

def enviarPDF(caminhos_arquivos):
    global idUser

    url = "http://localhost/envioDocumento/backend/public/api/enviar-documento"
    
    # Criar uma lista de arquivos para enviar
    files = [('files[]', (os.path.basename(caminho_arquivo), open(caminho_arquivo, 'rb'))) for caminho_arquivo in caminhos_arquivos]
    data = {
        'id': idUser,
    }

    try:
        response = requests.post(url, files=files, data=data)

        # Verificar se a resposta está em JSON
        try:
            response_json = response.json()
            if 'error' in response_json:
                error_msg = response_json['error']
                messagebox.showerror("Erro", f"Erro ao enviar os arquivos. {error_msg} \n Entre em contato com o número: (31) 98915-9131")
            else:
                response_text = json.dumps(response_json, ensure_ascii=False, indent=4)
                if response.status_code == 200:
                    messagebox.showinfo("Sucesso", "Arquivos enviados com sucesso!")
                    print(f"Resposta da API: {response_text}")
                elif response.status_code == 207:
                    error_msg = response_json['erros']['erro']
                    messagebox.showwarning("Alerta", f"Alguns não foram enviados: \n {error_msg}")
                    print(f"Resposta da API: {response_text}")
                else:
                    messagebox.showerror("Erro", f"Erro ao enviar os arquivos. {error_msg} \n Entre em contato com o número: (31) 98915-9131")
                    print(f"Erro ao enviar os arquivos. Status Code: {response.status_code}")
        except ValueError:
            response_text = response.text
            print(f"Erro ao enviar os arquivos. Resposta da API não é um JSON. {response_text}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao enviar os arquivos: {e} \n Entre em contato com o número: (31) 98915-9131")
        print(f"Erro ao enviar os arquivos: {e}")

def abrir_pasta():
    diretorio_atual = os.getcwd()
    pasta_docs = os.path.join(diretorio_atual, "CLIENTE")
    
    if os.path.exists(pasta_docs) and os.path.isdir(pasta_docs):
        diretorio_para_abrir = pasta_docs
    else:
        diretorio_para_abrir = diretorio_atual
    
    subprocess.Popen(f'explorer {os.path.realpath(diretorio_para_abrir)}')

def formLogin():
    global janela, email, password, emailLabel, passwordLabel, botao_avancar

    emailLabel = Label(janela, text='Email:', anchor='center')
    emailLabel.place(x=70, y=120)
    email = Entry(justify='left')
    email.place(x=200, y=120)
    emailLabel.configure(bg='#cf9416')

    passwordLabel = Label(janela, text='Senha:', anchor='center')
    passwordLabel.place(x=70, y=150)
    password = Entry(justify='left', show='*')
    password.place(x=200, y=150)
    passwordLabel.configure(bg='#cf9416')

    def validarLogin():
        url = "http://localhost/envioDocumento/backend/public/api/login"
        global idUser, logado

        data ={
            'email': email.get(),
            'password': password.get()
        }

        response = requests.post(url, data=data)

        try:
            try:
                response_json = response.json()
                if 'message' in response_json:
                    error_msg = response_json['message']
                else:
                    response_text = json.dumps(response_json, ensure_ascii=False, indent=4)
            except ValueError:
                response_text = response.text
                
            if response.status_code == 200:
                logado = True
                idUser = response_json['user']['id']
                messagebox.showinfo("Sucesso", "Login efetuado com sucesso!")
                print(f"Resposta da API: {response_text}")
                atualizar_interface()
            else:
                logado = False
                messagebox.showerror("Erro", f"{error_msg}")
        except Exception as e:
            logado = False
            messagebox.showerror("Erro", f"Não foi possível efetuar o login: {e} \n Entre em contato com o número: (31) 8915-9131")
            print(f"Erro {e}")
    
    botao_avancar = tk.Button(janela, text="Avançar", command=validarLogin)
    botao_avancar.place(x=200, y=180)
    global idUser

def enviar(departamento):
    global arquivosUpload
    
    if departamento == "":
        messagebox.showerror("Erro", "Escolha um departamento")
        return
    
    criarDiretorios(arquivosUpload, departamento)
   
def atualizar_interface():
    global emailLabel, email, passwordLabel, password, botao_avancar

    if logado:
        # Remover campos de login
        emailLabel.place_forget()
        email.place_forget()
        passwordLabel.place_forget()
        password.place_forget()
        botao_avancar.place_forget()
    
        # Criar um botão para selecionar o arquivo e converter
        botao_selecionar = tk.Button(janela, text="Selecionar PDF", command=selecionarPdf)
        botao_selecionar.pack(pady=20)

        global label
        #label = tk.Label(janela, text="Nenhum arquivo selecionado")
        #label.pack(pady=20)

        label = tk.Label(janela, text="Ou arraste um arquivo aqui")
        label.pack(pady=20)

        janela.drop_target_register(DND_FILES)
        janela.dnd_bind('<<Drop>>', drop)

        label = tk.Label(janela, text="Escolha o departamento dos documentos")
        label.pack(pady=20)
        departamento = StringVar()
        departamento.set( "" )
        dep_menu = OptionMenu(janela, departamento, "FISCAL", "CONTABIL", "PESSOAL", "SOCIETARIO")
        dep_menu.place(x=160, y=200)

        botao_enviar_pdf = tk.Button(janela, text="ENVIAR", command=lambda: enviar(departamento.get()))
        botao_enviar_pdf.pack(pady=20)
        botao_enviar_pdf.place(x=160, y=250)
        botao_enviar_pdf.configure(bg='#2771d8')

        botao_abrir_pasta = tk.Button(janela, text="Abrir Pasta", command=abrir_pasta)
        botao_abrir_pasta.pack(pady=20)
        botao_abrir_pasta.place(x=160, y=300)

janela = TkinterDnD.Tk()
janela.title("Submissão de PDFs")
janela.geometry("400x340")
janela.resizable(height=False, width=False)
logado = FALSE

formLogin()

janela.mainloop()