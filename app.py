import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import zipfile
import io
import base64
from fpdf import FPDF

# Configuração da página da Barbearia com o nome oficial completo
st.set_page_config(page_title="O Chefão Barbearia e Conveniência", layout="wide", initial_sidebar_state="expanded")

# Bancos de dados em formato CSV
ARQUIVO_SERVICOS = "servicos.csv"
ARQUIVO_PRODUTOS = "produtos.csv"
ARQUIVO_VENDAS = "vendas.csv"
ARQUIVO_GASTOS = "gastos.csv"
ARQUIVO_BARBEIROS = "barbeiros.csv"
ARQUIVO_ASSINATURAS = "assinaturas.csv"
ARQUIVO_PRESENCAS = "presencas.csv"
ARQUIVO_USUARIOS = "usuarios.csv"
ARQUIVO_CONSUMO_INTERNO = "consumo_interno.csv"
ARQUIVO_FECHAMENTOS = "fechamentos.csv"
ARQUIVO_AUDITORIA = "auditoria.csv"

# Lista oficial para o Backup ZIP
TODOS_ARQUIVOS_BACKUP = {
    "vendas.csv": ARQUIVO_VENDAS,
    "gastos.csv": ARQUIVO_GASTOS,
    "barbeiros.csv": ARQUIVO_BARBEIROS,
    "assinaturas.csv": ARQUIVO_ASSINATURAS,
    "presencas.csv": ARQUIVO_PRESENCAS,
    "consumo_interno.csv": ARQUIVO_CONSUMO_INTERNO,
    "usuarios.csv": ARQUIVO_USUARIOS,
    "fechamentos.csv": ARQUIVO_FECHAMENTOS,
    "auditoria.csv": ARQUIVO_AUDITORIA
}

def inicializar_banco_de_dados():
    if not os.path.exists(ARQUIVO_SERVICOS):
        pd.DataFrame([
            {"ID": 1, "Nome do Serviço": "Corte Social", "Preço (R$)": 35.0},
            {"ID": 2, "Nome do Serviço": "Barba Completa", "Preço (R$)": 25.0},
            {"ID": 3, "Nome do Serviço": "Combo (Corte + Barba)", "Preço (R$)": 55.0}
        ]).to_csv(ARQUIVO_SERVICOS, index=False, encoding='utf-8')

    if not os.path.exists(ARQUIVO_PRODUTOS):
        pd.DataFrame([
            {"ID": 1, "Nome do Produto": "Pomada Modeladora", "Preço de Venda": 40.0, "Preço de Custo": 20.0, "Estoque Inicial": 10, "Estoque Atual": 10, "Comissão Barbeiro (R$)": 5.0},
            {"ID": 2, "Nome do Produto": "Cerveja Long Neck", "Preço de Venda": 8.0, "Preço de Custo": 4.0, "Estoque Inicial": 24, "Estoque Atual": 24, "Comissão Barbeiro (R$)": 0.0}
        ]).to_csv(ARQUIVO_PRODUTOS, index=False, encoding='utf-8')

    for arquivo in TODOS_ARQUIVOS_BACKUP.values():
        if not os.path.exists(arquivo):
            if arquivo == ARQUIVO_USUARIOS:
                pd.DataFrame([{"Usuario": "admin", "Senha": "barba123", "Permissoes": "TODAS"}]).to_csv(arquivo, index=False, encoding='utf-8')
            elif arquivo == ARQUIVO_BARBEIROS:
                pd.DataFrame([{"Nome": "G.", "Comissão (%)": 50.0}]).to_csv(arquivo, index=False, encoding='utf-8')
            elif arquivo == ARQUIVO_FECHAMENTOS:
                pd.DataFrame(columns=["Data", "Usuario", "Dinheiro Real", "Pix Real", "Cartao Real", "Total Real", "Total Sistema", "Diferenca", "Status", "Observacoes"]).to_csv(arquivo, index=False, encoding='utf-8')
            elif arquivo == ARQUIVO_AUDITORIA:
                pd.DataFrame(columns=["Horário Log", "Usuário Responsável", "Ação Realizada", "Detalhes do Item Deletado"]).to_csv(arquivo, index=False, encoding='utf-8')
            elif arquivo == ARQUIVO_VENDAS:
                pd.DataFrame(columns=["Data", "Item", "Tipo", "Quantidade", "Valor Total", "Forma de Pagamento", "Barbeiro", "Cliente"]).to_csv(arquivo, index=False, encoding='utf-8')
            elif arquivo == ARQUIVO_CONSUMO_INTERNO:
                pd.DataFrame(columns=["Data", "Responsavel", "Item", "Quantidade", "Valor Total"]).to_csv(arquivo, index=False, encoding='utf-8')
            elif arquivo == ARQUIVO_GASTOS:
                pd.DataFrame(columns=["Data", "Descrição", "Valor (R$)", "Categoria"]).to_csv(arquivo, index=False, encoding='utf-8')
            else:
                pd.DataFrame().to_csv(arquivo, index=False, encoding='utf-8')

inicializar_banco_de_dados()

usuarios_df = pd.read_csv(ARQUIVO_USUARIOS, encoding='utf-8')

PERMISSOES_MASTER = ["💸 Abrir Comanda (Vendas)", "🔍 Extrato de Fluxo", "💳 Clube de Assinaturas", "📉 Lançar Gasto/Despesa", "✏️ Corrigir Lançamentos", "🔒 Fechamento de Dia", "👥 Cadastrar Barbeiro", "📦 Estoque & Serviços", "⚙️ Gerenciar Catálogo", "👤 Gerenciar Usuários", "📊 Painel de Relatórios", "📄 Emitir Relatórios", "🕵️ Trilha de Auditoria", "💾 Backup do Sistema", "⚙️ Configurações"]
PERMISSOES_PADRAO = ["💸 Abrir Comanda (Vendas)", "🔍 Extrato de Fluxo", "📦 Estoque & Serviços"]

def registrar_rastro_auditoria(acao, detalhes):
    df_auditoria_atual = pd.read_csv(ARQUIVO_AUDITORIA, encoding='utf-8')
    nova_linha_log = pd.DataFrame([{
        "Horário Log": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Usuário Responsável": st.session_state["perfil"].upper(),
        "Ação Realizada": acao,
        "Detalhes do Item Deletado": detalhes
    }])
    pd.concat([df_auditoria_atual, nova_linha_log], ignore_index=True).to_csv(ARQUIVO_AUDITORIA, index=False, encoding='utf-8')

# --- SISTEMA DE LOGIN MULTI-USUÁRIO ---
def gerar_token(usuario):
    validade = (datetime.now() + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")
    texto = f"{usuario}|{validade}"
    return base64.b64encode(texto.encode('utf-8')).decode('utf-8')

def validar_token(token):
    try:
        texto = base64.b64decode(token.encode('utf-8')).decode('utf-8')
        usuario, validade_str = texto.split("|")
        validade = datetime.strptime(validade_str, "%Y-%m-%d %H:%M:%S")
        if datetime.now() <= validade: return usuario
    except: pass
    return None

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["perfil"] = None
    st.session_state["permissoes_usuario"] = PERMISSOES_PADRAO
    st.session_state["carrinho_comanda"] = []

if not st.session_state["autenticado"] and "token" in st.query_params:
    usr_decodificado = validar_token(st.query_params["token"])
    if usr_decodificado:
        usuarios_df["Usuario_Lower"] = usuarios_df["Usuario"].str.strip().str.lower()
        u_linha = usuarios_df[usuarios_df["Usuario_Lower"] == usr_decodificado.strip().lower()]
        if not u_linha.empty:
            st.session_state["autenticado"] = True
            st.session_state["perfil"] = usr_decodificado
            perm_string = u_linha.iloc[0]["Permissoes"]
            st.session_state["permissoes_usuario"] = PERMISSOES_MASTER if perm_string == "TODAS" else perm_string.split("|")

if not st.session_state["autenticado"]:
    st.title("💈 O Chefão Barbearia e Conveniência")
    col_login, _ = st.columns([1, 2])
    with col_login:
        with st.container(border=True):
            input_usuario = st.text_input("Usuário:").strip().lower()
            input_senha = st.text_input("Senha:", type="password")
            if st.button("🔓 Acessar Sistema", type="primary", use_container_width=True):
                usuarios_df["Usuario_Lower"] = usuarios_df["Usuario"].str.strip().str.lower()
                usuario_valido = usuarios_df[(usuarios_df["Usuario_Lower"] == input_usuario) & (usuarios_df["Senha"] == input_senha)]
                if not usuario_valido.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["perfil"] = input_usuario
                    st.query_params["token"] = gerar_token(input_usuario)
                    perm_string = usuario_valido.iloc[0]["Permissoes"]
                    st.session_state["permissoes_usuario"] = PERMISSOES_MASTER if perm_string == "TODAS" else perm_string.split("|")
                    st.rerun()
                else: st.error("Usuário ou senha incorretos!")
    st.stop()

servicos_df = pd.read_csv(ARQUIVO_SERVICOS, encoding='utf-8')
produtos_df = pd.read_csv(ARQUIVO_PRODUTOS, encoding='utf-8')
vendas_df = pd.read_csv(ARQUIVO_VENDAS, encoding='utf-8').dropna(how='all')
gastos_df = pd.read_csv(ARQUIVO_GASTOS, encoding='utf-8').dropna(how='all')
barbeiros_df = pd.read_csv(ARQUIVO_BARBEIROS, encoding='utf-8').dropna(how='all')
assinaturas_df = pd.read_csv(ARQUIVO_ASSINATURAS, encoding='utf-8').dropna(how='all')
presencas_df = pd.read_csv(ARQUIVO_PRESENCAS, encoding='utf-8').dropna(how='all')
consumo_interno_df = pd.read_csv(ARQUIVO_CONSUMO_INTERNO, encoding='utf-8').dropna(how='all')
fechamentos_df = pd.read_csv(ARQUIVO_FECHAMENTOS, encoding='utf-8').dropna(how='all')
auditoria_df = pd.read_csv(ARQUIVO_AUDITORIA, encoding='utf-8').dropna(how='all')

st.sidebar.title("✂️ O Chefão")
st.sidebar.write(f"Conectado como: **{st.session_state['perfil'].upper()}**")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegação:", st.session_state["permissoes_usuario"])
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair com Segurança", use_container_width=True):
    st.session_state["autenticado"] = False
    st.session_state["perfil"] = None
    st.session_state["permissoes_usuario"] = []
    st.session_state["carrinho_comanda"] = []
    st.query_params.clear()
    st.rerun()

class PDFRelatorio(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "O CHEFAO BARBEARIA E CONVENIENCIA", ln=1, align="C")
        self.set_font("Arial", "I", 10)
        self.cell(0, 5, "Relatorio Oficial de Movimentacao de Caixa e Auditoria", ln=1, align="C")
        self.ln(5)
        self.line(10, 26, 200, 26)
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

# ---------------- MÓDULO 1: COMANDA ELETRÔNICA ----------------
if menu == "💸 Abrir Comanda (Vendas)":
    st.header("📋 Caixa e Comanda Eletrônica - O Chefão")
    col_com1, col_com2 = st.columns([1, 1], gap="large")
    with col_com1:
        with st.container(border=True):
            st.subheader("➕ Adicionar Item")
            tipo = st.selectbox("Selecione a Categoria:", ["Serviço (Corte/Barba)", "Produto (Bebida/Pomada)"])
            lista_itens = servicos_df["Nome do Serviço"].tolist() if tipo == "Serviço (Corte/Barba)" else produtos_df["Nome do Produto"].tolist()
            tabela_ref = servicos_df if tipo == "Serviço (Corte/Barba)" else produtos_df
            nome_col_preco = "Preço (R$)" if tipo == "Serviço (Corte/Barba)" else "Preço de Venda"
            categoria_venda = "Serviço" if tipo == "Serviço (Corte/Barba)" else "Produto"
            item_selecionado = st.selectbox("Selecione o Item do Catálogo:", lista_itens)
            qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1)
            preco_unitario = tabela_ref[tabela_ref.iloc[:, 1] == item_selecionado][nome_col_preco].values[0]
            subtotal_item = float(preco_unitario) * qtd
            st.write(f"**Subtotal do item:** R$ {subtotal_item:.2f}")
            
            pode_adicionar = True
            if tipo == "Produto (Bebida/Pomada)":
                est_atual_conf = produtos_df[produtos_df["Nome do Produto"] == item_selecionado]["Estoque Atual"].values[0]
                if qtd > est_atual_conf:
                    st.error(f"Estoque insuficiente! Disponível apenas: {est_atual_conf} unidades.")
                    pode_adicionar = False
                    
            if st.button("➕ Inserir na Comanda", use_container_width=True, disabled=not pode_adicionar):
                st.session_state["carrinho_comanda"].append({"Item": item_selecionado, "Tipo": categoria_venda, "Quantidade": qtd, "Valor Total": subtotal_item})
                st.rerun()
    with col_com2:
        with st.container(border=True):
            st.subheader("🛒 Resumo Consumo")
            if len(st.session_state["carrinho_comanda"]) > 0:
                df_temp_carrinho = pd.DataFrame(st.session_state["carrinho_comanda"])
                st.dataframe(df_temp_carrinho, use_container_width=True, hide_index=True)
                valor_total_comanda = df_temp_carrinho["Valor Total"].sum()
                st.markdown(
