import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="O Chefão - Barbearia", layout="wide")

# Arquivos
ARQUIVO_USUARIOS = "usuarios.csv"

# Inicialização de segurança
if not os.path.exists(ARQUIVO_USUARIOS):
    pd.DataFrame([{"Usuario": "admin", "Senha": "barba123", "Permissoes": "TODAS"}]).to_csv(ARQUIVO_USUARIOS, index=False)

usuarios_df = pd.read_csv(ARQUIVO_USUARIOS)
PERMISSOES_MASTER = ["💸 Abrir Comanda", "👤 Gerenciar Usuários"] # Adicione as outras conforme necessário

# --- LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("Login - O Chefão")
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        u_db = usuarios_df[usuarios_df["Usuario"] == user]
        if not u_db.empty and u_db.iloc[0]["Senha"] == pwd:
            st.session_state.update({"logado": True, "perfil": user, "perms": u_db.iloc[0]["Permissoes"]})
            st.rerun()
    st.stop()

# --- NAVEGAÇÃO SEGURA ---
st.sidebar.write(f"Olá, {st.session_state.perfil}")
menu = st.sidebar.radio("Menu", st.session_state.perms.split("|") if st.session_state.perms != "TODAS" else PERMISSOES_MASTER)

if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# --- TELA GERENCIAR USUÁRIOS (Sem conflito de Keys) ---
if menu == "👤 Gerenciar Usuários":
    st.header("Gerenciar Usuários")
    aba1, aba2 = st.tabs(["Criar", "Editar"])
    
    with aba1:
        n_u = st.text_input("Usuário", key="n_u")
        n_p = st.text_input("Senha", key="n_p")
        if st.button("Salvar Novo"):
            new_u = pd.DataFrame([{"Usuario": n_u, "Senha": n_p, "Permissoes": "💸 Abrir Comanda"}])
            pd.concat([usuarios_df, new_u]).to_csv(ARQUIVO_USUARIOS, index=False)
            st.success("Criado!")
    
    with aba2:
        st.write("Editar usuários aqui...")
