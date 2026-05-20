import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import zipfile
import io
import base64

# Configuração da página
st.set_page_config(page_title="O Chefão Barbearia", layout="wide")

# Bancos de dados
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

TODOS_ARQUIVOS_BACKUP = {
    "vendas.csv": ARQUIVO_VENDAS, "gastos.csv": ARQUIVO_GASTOS,
    "barbeiros.csv": ARQUIVO_BARBEIROS, "assinaturas.csv": ARQUIVO_ASSINATURAS,
    "presencas.csv": ARQUIVO_PRESENCAS, "consumo_interno.csv": ARQUIVO_CONSUMO_INTERNO,
    "usuarios.csv": ARQUIVO_USUARIOS, "fechamentos.csv": ARQUIVO_FECHAMENTOS
}

# Inicialização simplificada
for arquivo in TODOS_ARQUIVOS_BACKUP.values():
    if not os.path.exists(arquivo):
        if arquivo == ARQUIVO_USUARIOS: pd.DataFrame([{"Usuario": "admin", "Senha": "barba123", "Permissoes": "TODAS"}]).to_csv(arquivo, index=False)
        else: pd.DataFrame().to_csv(arquivo, index=False)
if not os.path.exists(ARQUIVO_SERVICOS): pd.DataFrame(columns=["ID", "Nome do Serviço", "Preço (R$)"]).to_csv(ARQUIVO_SERVICOS, index=False)
if not os.path.exists(ARQUIVO_PRODUTOS): pd.DataFrame(columns=["ID", "Nome do Produto", "Preço de Venda", "Preço de Custo", "Estoque Inicial", "Comissão Barbeiro (R$)"]).to_csv(ARQUIVO_PRODUTOS, index=False)

usuarios_df = pd.read_csv(ARQUIVO_USUARIOS, encoding='utf-8')
PERMISSOES_MASTER = ["💸 Abrir Comanda (Vendas)", "💳 Clube de Assinaturas", "📉 Lançar Gasto/Despesa", "✏️ Corrigir Lançamentos", "🔒 Fechamento de Dia", "👥 Cadastrar Barbeiro", "📦 Estoque & Serviços", "⚙️ Gerenciar Catálogo", "👤 Gerenciar Usuários", "📊 Painel de Relatórios", "💾 Backup do Sistema", "⚙️ Configurações"]

# --- LOGIN SIMPLIFICADO ---
if "autenticado" not in st.session_state: st.session_state.update({"autenticado": False, "perfil": None, "permissoes_usuario": []})

if not st.session_state["autenticado"]:
    st.title("💈 O Chefão Barbearia")
    u = st.text_input("Usuário:").strip().lower()
    p = st.text_input("Senha:", type="password")
    if st.button("Acessar"):
        user = usuarios_df[usuarios_df["Usuario"].str.lower() == u]
        if not user.empty and user.iloc[0]["Senha"] == p:
            st.session_state.update({"autenticado": True, "perfil": u, "permissoes_usuario": PERMISSOES_MASTER if user.iloc[0]["Permissoes"] == "TODAS" else user.iloc[0]["Permissoes"].split("|")})
            st.rerun()
        else: st.error("Erro!")
    st.stop()

# --- NAVEGAÇÃO ---
menu = st.sidebar.radio("Navegação:", st.session_state["permissoes_usuario"])
if st.sidebar.button("Sair"):
    st.session_state.update({"autenticado": False})
    st.rerun()

# --- MÓDULO GERENCIAR USUÁRIOS (Corrigido para não dar erro) ---
if menu == "👤 Gerenciar Usuários" and st.session_state["perfil"] == "admin":
    st.header("👤 Gerenciamento de Usuários")
    aba1, aba2 = st.tabs(["➕ Criar", "✏️ Editar"])
    with aba1:
        n_u = st.text_input("Novo Usuário:", key="n_u_1")
        n_p = st.text_input("Senha:", type="password", key="n_p_1")
        # Listagem de checkboxes com keys únicas
        checks = {p: st.checkbox(p, key=f"c_{i}") for i, p in enumerate(PERMISSOES_MASTER)}
        if st.button("Salvar Novo"):
            p_str = "|".join([k for k, v in checks.items() if v])
            usuarios_df = pd.concat([usuarios_df, pd.DataFrame([{"Usuario": n_u, "Senha": n_p, "Permissoes": p_str}])], ignore_index=True)
            usuarios_df.to_csv(ARQUIVO_USUARIOS, index=False)
            st.rerun()
    with aba2:
        usr_sel = st.selectbox("Usuário:", usuarios_df[usuarios_df["Usuario"] != "admin"]["Usuario"])
        if usr_sel:
            row = usuarios_df[usuarios_df["Usuario"] == usr_sel].iloc[0]
            edit_p = st.text_input("Nova Senha:", value=row["Senha"], key="e_p")
            edit_checks = {p: st.checkbox(p, value=(p in str(row["Permissoes"])), key=f"e_{i}") for i, p in enumerate(PERMISSOES_MASTER)}
            if st.button("Salvar Alterações"):
                p_str = "|".join([k for k, v in edit_checks.items() if v])
                usuarios_df.loc[usuarios_df["Usuario"] == usr_sel, ["Senha", "Permissoes"]] = [edit_p, p_str]
                usuarios_df.to_csv(ARQUIVO_USUARIOS, index=False)
                st.success("Salvo!")
                st.rerun()

# (Inclua os outros módulos aqui, garantindo que o resto do código siga o padrão de navegação...)
