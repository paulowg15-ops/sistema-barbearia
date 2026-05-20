import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="O Chefão Barbearia", layout="wide")

# ARQUIVOS
ARQUIVO_USUARIOS = "usuarios.csv"
ARQUIVO_VENDAS = "vendas.csv"

# Inicialização mínima
if not os.path.exists(ARQUIVO_USUARIOS):
    pd.DataFrame([{"Usuario": "admin", "Senha": "barba123", "Permissoes": "TODAS"}]).to_csv(ARQUIVO_USUARIOS, index=False)

usuarios_df = pd.read_csv(ARQUIVO_USUARIOS)

# --- LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("💈 O Chefão - Login")
    u = st.text_input("Usuário", key="login_u")
    p = st.text_input("Senha", type="password", key="login_p")
    if st.button("Entrar"):
        user = usuarios_df[usuarios_df["Usuario"] == u]
        if not user.empty and user.iloc[0]["Senha"] == p:
            st.session_state.update({"logado": True, "perfil": u, "perms": user.iloc[0]["Permissoes"]})
            st.rerun()
        else: st.error("Usuário ou senha inválidos!")
    st.stop()

# --- MENU COM KEYS ÚNICAS ---
PERMISSOES_COMPLETAS = ["💸 Abrir Comanda", "💳 Clube Assinatura", "📉 Lançar Gastos", "✏️ Corrigir", "🔒 Fechamento", "👥 Barbeiros", "📦 Estoque", "⚙️ Catálogo", "👤 Gerenciar Usuários", "📊 Relatórios", "💾 Backup", "⚙️ Config"]
lista_menu = PERMISSOES_COMPLETAS if st.session_state.perms == "TODAS" else st.session_state.perms.split("|")

menu = st.sidebar.radio("Navegação:", lista_menu)

if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

# --- TELA GERENCIAR USUÁRIOS (Corrigida) ---
if menu == "👤 Gerenciar Usuários" and st.session_state.perfil == "admin":
    st.header("👤 Gerenciar Usuários")
    aba1, aba2 = st.tabs(["Criar", "Editar"])
    
    with aba1:
        n_u = st.text_input("Novo Usuário", key="criar_u")
        n_p = st.text_input("Nova Senha", type="password", key="criar_p")
        checks = {p: st.checkbox(p, key=f"check_criar_{i}") for i, p in enumerate(PERMISSOES_COMPLETAS)}
        if st.button("Salvar Novo Usuário"):
            p_str = "|".join([k for k, v in checks.items() if v])
            new_u = pd.DataFrame([{"Usuario": n_u, "Senha": n_p, "Permissoes": p_str}])
            pd.concat([usuarios_df, new_u], ignore_index=True).to_csv(ARQUIVO_USUARIOS, index=False)
            st.success("Usuário criado!")
            st.rerun()

    with aba2:
        usr_sel = st.selectbox("Selecione o usuário:", usuarios_df[usuarios_df["Usuario"] != "admin"]["Usuario"])
        if usr_sel:
            row = usuarios_df[usuarios_df["Usuario"] == usr_sel].iloc[0]
            e_p = st.text_input("Senha", value=row["Senha"], key="edit_p")
            e_checks = {p: st.checkbox(p, value=(p in str(row["Permissoes"])), key=f"check_edit_{i}") for i, p in enumerate(PERMISSOES_COMPLETAS)}
            if st.button("Salvar Alterações"):
                p_str = "|".join([k for k, v in e_checks.items() if v])
                usuarios_df.loc[usuarios_df["Usuario"] == usr_sel, ["Senha", "Permissoes"]] = [e_p, p_str]
                usuarios_df.to_csv(ARQUIVO_USUARIOS, index=False)
                st.success("Alterado!")
                st.rerun()

# Adicione os outros módulos (Vendas, Estoque, etc) aqui embaixo exatamente como estavam
