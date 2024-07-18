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
    url = "http://localhost/envioDocumento/backend/public/api/enviar-documento"

    try:
        with open(caminho_arquivo, 'rb') as file:
            files = {'file': file}
            data = {
                'id': 1,
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
                messagebox.showerror("Erro", f"Erro ao enviar o arquivo. {error_msg}")
                print(f"Erro ao enviar o arquivo. Status Code: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao enviar o arquivo: {e}")
        print(f"Erro ao enviar o arquivo: {e}")

def abrir_pasta():
    diretorio_atual = os.getcwd()
    pasta_docs = os.path.join(diretorio_atual, "CLIENTE")
    
    if os.path.exists(pasta_docs) and os.path.isdir(pasta_docs):
        diretorio_para_abrir = pasta_docs
    else:
        diretorio_para_abrir = diretorio_atual
    
    subprocess.Popen(f'explorer {os.path.realpath(diretorio_para_abrir)}')

def login():
    #Criação dos labels e campos
    lbl1 = Label(janela, text='Quantidade de páginas', anchor='center')
    lbl1.place(x=70, y=120)
    ent1 = Entry(justify='center')
    ent1.place(x=200, y=120)
    lbl1.configure(bg='#cf9416')

#janela = tk.Tk()
janela = TkinterDnD.Tk()
janela.title("Submissão de PDFs")
janela.geometry("400x300")
janela.resizable(height=False, width=False)

# Criar um botão para selecionar o arquivo e converter
botao_converter = tk.Button(janela, text="Selecionar PDF", command=selecionarPdf)
botao_converter.pack(pady=20)

label = tk.Label(janela, text="Nenhum arquivo selecionado")
label.pack(pady=20)

label = tk.Label(janela, text="Ou arraste um arquivo aqui")
label.pack(pady=20)

janela.drop_target_register(DND_FILES)
janela.dnd_bind('<<Drop>>', drop)

botao_abrir_pasta = tk.Button(janela, text="Abrir Pasta", command=abrir_pasta)
botao_abrir_pasta.pack(pady=20)
#login()

janela.mainloop()