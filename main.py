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

idUser = 0
logado = False

def drop(event):
    # Obter o caminho do arquivo arrastado
    caminho_arquivo = event.data
    label.config(text=f"Arquivo selecionado: {caminho_arquivo}")

    extensao = os.path.splitext(caminho_arquivo)[1]
    if extensao.lower() != ".pdf":
        messagebox.showerror("Erro", "Por favor, selecione um arquivo PDF.")
        return

    criarDiretorios(caminho_arquivo)

def selecionar_arquivo():
    caminho_arquivo = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if caminho_arquivo:
        label.config(text=f"Arquivo selecionado: {caminho_arquivo}")
        return caminho_arquivo
    else:
        label.config(text="Nenhum arquivo selecionado")
        return None
    
def selecionarPdf():
    caminho_arquivo = selecionar_arquivo()
    if not caminho_arquivo:
        return
    
    # Verificar se a extensão do arquivo é .pdf
    extensao = os.path.splitext(caminho_arquivo)[1]
    if extensao.lower() != ".pdf":
        messagebox.showerror("Erro", "Por favor, selecione um arquivo PDF.")
        return
    
    criarDiretorios(caminho_arquivo)

def criarDiretorios(caminho_arquivo):
    label.config(text="Enviando arquivo. Aguarde...")

    # Determinar o diretório onde o script Python está localizado
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))

    # Criar uma pasta específica dentro do diretório atual
    pasta_cliente = os.path.join(diretorio_atual, "CLIENTE")
    if not os.path.exists(pasta_cliente):
        os.makedirs(pasta_cliente)

    # Dentro da pasta CLIENTE, criar a pasta "fiscal" se não existir
    pasta_fiscal = os.path.join(pasta_cliente, "fiscal")
    if not os.path.exists(pasta_fiscal):
        os.makedirs(pasta_fiscal)

    # Determinar o ano corrente
    ano_corrente = datetime.now().year
    pasta_ano = os.path.join(pasta_fiscal, str(ano_corrente))
    if not os.path.exists(pasta_ano):
        os.makedirs(pasta_ano)

    # Determinar o mês corrente
    mes_corrente = datetime.now().month
    pasta_mes = os.path.join(pasta_ano, str(mes_corrente))
    if not os.path.exists(pasta_mes):
        os.makedirs(pasta_mes)

    # Caminho do arquivo de destino na pasta mes
    nome_arquivo = os.path.basename(caminho_arquivo)
    caminho_destino = os.path.join(pasta_mes, nome_arquivo)

    try:
        shutil.copy(caminho_arquivo, caminho_destino)
        enviarPDF(caminho_destino)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar o arquivo: {e}")
    finally:
        label.config(text='')

def enviarPDF(caminho_arquivo):
    global idUser
    url = "http://localhost/envioDocumento/backend/public/api/enviar-documento"

    try:
        with open(caminho_arquivo, 'rb') as file:
            files = {'file': file}
            data = {
                'id': idUser,
            }

            response = requests.post(url, files=files, data=data)

            # Verificar se a resposta está em JSON
            try:
                response_json = response.json()
                if 'error' in response_json:
                    error_msg = response_json['error']
                else:
                    response_text = json.dumps(response_json, ensure_ascii=False, indent=4)
            except ValueError:
                response_text = response.text

            if response.status_code == 200:
                messagebox.showinfo("Sucesso", "Arquivo enviado com sucesso!")
                print(f"Resposta da API: {response_text}")
            else:
                messagebox.showerror("Erro", f"Erro ao enviar o arquivo. {error_msg} \n Entre em contato com o número: (31) 8915-9131")
                print(f"Erro ao enviar o arquivo. Status Code: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao enviar o arquivo: {e} \n Entre em contato com o número: (31) 8915-9131")
        print(f"Erro ao enviar o arquivo: {e}")

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
        label = tk.Label(janela, text="Nenhum arquivo selecionado")
        label.pack(pady=20)

        label = tk.Label(janela, text="Ou arraste um arquivo aqui")
        label.pack(pady=20)

        janela.drop_target_register(DND_FILES)
        janela.dnd_bind('<<Drop>>', drop)

        botao_abrir_pasta = tk.Button(janela, text="Abrir Pasta", command=abrir_pasta)
        botao_abrir_pasta.pack(pady=20)

#janela = tk.Tk()
janela = TkinterDnD.Tk()
janela.title("Submissão de PDFs")
janela.geometry("400x300")
janela.resizable(height=False, width=False)
logado = FALSE

formLogin()

janela.mainloop()