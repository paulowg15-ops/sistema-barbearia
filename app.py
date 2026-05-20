import streamlit as st
import pandas as pd
import os
import zipfile
import io
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="O Chefão Barbearia", layout="wide")

# Arquivos
FILES = {
    "servicos": "servicos.csv", "produtos": "produtos.csv", "vendas": "vendas.csv",
    "gastos": "gastos.csv", "barbeiros": "barbeiros.csv", "assinaturas": "assinaturas.csv",
    "presencas": "presencas.csv", "usuarios": "usuarios.csv", "consumo": "consumo_interno.csv",
    "fechamentos": "fechamentos.csv"
}

# Inicialização de arquivos
for k, v in FILES.items():
    if not os.path.exists(v):
        pd.DataFrame().to_csv(v, index=False)
if not os.path.exists(FILES["usuarios"]):
    pd.DataFrame([{"Usuario": "admin", "Senha": "123", "Permissoes": "TODAS"}]).to_csv(FILES["usuarios"], index=False)

# Carregamento de dados
usuarios_df = pd.read_csv(FILES["usuarios"])
vendas_df = pd.read_csv(FILES["vendas"])

# --- LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("💈 Login - O Chefão")
    u = st.text_input("Usuário")
    p = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = usuarios_df[usuarios_df["Usuario"] == u]
        if not user.empty and user.iloc[0]["Senha"] == p:
            st.session_state.update({"logado": True, "perfil": u, "perms": user.iloc[0]["Permissoes"]})
            st.rerun()
    st.stop()

# --- MENU LATERAL ---
PERMISSOES_LIST = ["💸 Comanda", "📊 Relatórios", "👤 Gerenciar Usuários", "💾 Backup"]
lista_menu = PERMISSOES_LIST if st.session_state.perms == "TODAS" else st.session_state.perms.split("|")
menu = st.sidebar.radio("Navegação:", lista_menu)

if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# --- TELA GERENCIAR USUÁRIOS (Corrigida com Keys Fixas) ---
if menu == "👤 Gerenciar Usuários":
    st.header("👤 Gerenciamento de Acessos")
    aba1, aba2 = st.tabs(["➕ Criar", "✏️ Editar"])
    
    with aba1:
        n_u = st.text_input("Novo Usuário", key="n_u_new")
        n_p = st.text_input("Senha", type="password", key="n_p_new")
        # Checkboxes com keys fixas para não dar duplicidade
        checks = {p: st.checkbox(p, key=f"c_{p}") for p in PERMISSOES_LIST}
        if st.button("Salvar Novo"):
            p_str = "|".join([k for k, v in checks.items() if v])
            pd.concat([usuarios_df, pd.DataFrame([{"Usuario": n_u, "Senha": n_p, "Permissoes": p_str}])]).to_csv(FILES["usuarios"], index=False)
            st.rerun()
            
    with aba2:
        usr_sel = st.selectbox("Selecione o usuário:", usuarios_df[usuarios_df["Usuario"] != "admin"]["Usuario"])
        if usr_sel:
            row = usuarios_df[usuarios_df["Usuario"] == usr_sel].iloc[0]
            e_p = st.text_input("Senha", value=row["Senha"], key="e_p_edit")
            e_checks = {p: st.checkbox(p, value=(p in str(row["Permissoes"])), key=f"e_{p}") for p in PERMISSOES_LIST}
            if st.button("Salvar Alterações"):
                p_str = "|".join([k for k, v in e_checks.items() if v])
                usuarios_df.loc[usuarios_df["Usuario"] == usr_sel, ["Senha", "Permissoes"]] = [e_p, p_str]
                usuarios_df.to_csv(FILES["usuarios"], index=False)
                st.success("Salvo!")
                st.rerun()
