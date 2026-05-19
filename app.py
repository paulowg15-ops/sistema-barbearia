import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

# Configuração da página da Barbearia
st.set_page_config(page_title="Barbearia - Sistema Avançado", layout="wide")

# Bancos de dados em formato CSV
ARQUIVO_SERVICOS = "servicos.csv"
ARQUIVO_PRODUTOS = "produtos.csv"
ARQUIVO_VENDAS = "vendas.csv"
ARQUIVO_GASTOS = "gastos.csv"
ARQUIVO_BARBEIROS = "barbeiros.csv"

# Função para garantir que todas as tabelas existam com dados iniciais
def inicializar_banco_de_dados():
    if not os.path.exists(ARQUIVO_SERVICOS):
        pd.DataFrame([
            {"ID": 1, "Nome do Serviço": "Corte Social", "Preço (R$)": 35.0},
            {"ID": 2, "Nome do Serviço": "Barba Completa", "Preço (R$)": 25.0},
            {"ID": 3, "Nome do Serviço": "Combo (Corte + Barba)", "Preço (R$)": 55.0},
            {"ID": 4, "Nome do Serviço": "Acabamento / Pezinho", "Preço (R$)": 15.0},
            {"ID": 5, "Nome do Serviço": "Platinado / Nevou", "Preço (R$)": 80.0}
        ]).to_csv(ARQUIVO_SERVICOS, index=False, encoding='utf-8')

    if not os.path.exists(ARQUIVO_PRODUTOS):
        pd.DataFrame([
            {"ID": 1, "Nome do Produto": "Pomada Modeladora", "Preço de Venda": 40.0, "Preço de Custo": 20.0, "Estoque Inicial": 10, "Comissão Barbeiro (R$)": 5.0},
            {"ID": 2, "Nome do Produto": "Cerveja Long Neck", "Preço de Venda": 8.0, "Preço de Custo": 4.0, "Estoque Inicial": 24, "Comissão Barbeiro (R$)": 0.0},
            {"ID": 3, "Nome do Produto": "Refrigerante Lata", "Preço de Venda": 5.0, "Preço de Custo": 2.5, "Estoque Inicial": 24, "Comissão Barbeiro (R$)": 0.0},
            {"ID": 4, "Nome do Produto": "Água Mineral", "Preço de Venda": 3.0, "Preço de Custo": 1.0, "Estoque Inicial": 10, "Comissão Barbeiro (R$)": 0.0},
            {"ID": 5, "Nome do Produto": "Óleo para Barba", "Preço de Venda": 35.0, "Preço de Custo": 18.0, "Estoque Inicial": 5, "Comissão Barbeiro (R$)": 3.0}
        ]).to_csv(ARQUIVO_PRODUTOS, index=False, encoding='utf-8')

    if not os.path.exists(ARQUIVO_VENDAS):
        pd.DataFrame(columns=["Data", "Item", "Tipo", "Quantidade", "Valor Total", "Forma de Pagamento", "Barbeiro", "Cliente"]).to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')

    if not os.path.exists(ARQUIVO_GASTOS):
        pd.DataFrame(columns=["Data", "Descrição", "Valor (R$)", "Categoria"]).to_csv(ARQUIVO_GASTOS, index=False, encoding='utf-8')

    if not os.path.exists(ARQUIVO_BARBEIROS):
        pd.DataFrame([
            {"Nome": "G.", "Comissão (%)": 50.0}
        ]).to_csv(ARQUIVO_BARBEIROS, index=False, encoding='utf-8')

inicializar_banco_de_dados()

# Carregar os dados atuais
servicos_df = pd.read_csv(ARQUIVO_SERVICOS, encoding='utf-8')
produtos_df = pd.read_csv(ARQUIVO_PRODUTOS, encoding='utf-8')
if "Comissão Barbeiro (R$)" not in produtos_df.columns:
    produtos_df["Comissão Barbeiro (R$)"] = 0.0

vendas_df = pd.read_csv(ARQUIVO_VENDAS, encoding='utf-8')
gastos_df = pd.read_csv(ARQUIVO_GASTOS, encoding='utf-8')
barbeiros_df = pd.read_csv(ARQUIVO_BARBEIROS, encoding='utf-8')

# --- SESSÃO DE LOGIN DE SEGURANÇA ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "perfil" not in st.session_state:
    st.session_state["perfil"] = None

if not st.session_state["autenticado"]:
    st.title("💈 Acesso ao Sistema - Barbearia")
    st.markdown("---")
    col_login, _ = st.columns([1, 2])
    with col_login:
        usuario = st.text_input("Usuário:")
        senha = st.text_input("Senha:", type="password")
        if st.button("Entrar", type="primary"):
            if usuario == "admin" and senha == "barba123":
                st.session_state["autenticado"] = True
                st.session_state["perfil"] = "admin"
                st.rerun()
            elif usuario == "barbeiro" and senha == "corte123":
                st.session_state["autenticado"] = True
                st.session_state["perfil"] = "barbeiro"
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")
    st.stop()

# --- CONTROLE DE MENUS POR PERFIL ---
if st.session_state["perfil"] == "admin":
    opcoes_menu = ["💸 Lançar Venda", "📉 Lançar Gasto/Despesa", "👥 Cadastrar Barbeiro", "📦 Estoque & Serviços", "⚙️ Gerenciar Catálogo", "📊 Painel de Relatórios", "⚙️ Configurações"]
else:
    opcoes_menu = ["💸 Lançar Venda", "📦 Estoque & Serviços"]

menu = st.sidebar.radio("Navegação", opcoes_menu)

st.sidebar.markdown("---")
st.sidebar.write(f"Conectado como: **{st.session_state['perfil'].upper()}**")
if st.sidebar.button("🚪 Sair do Sistema"):
    st.session_state["autenticado"] = False
    st.session_state["perfil"] = None
    st.rerun()

# ---------------- MÓDULO 1: LANÇAR VENDA ----------------
if menu == "💸 Lançar Venda":
    st.header("Registrar Atendimento / Venda")
    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox("Tipo de Venda:", ["Serviço (Corte/Barba)", "Produto (Bebida/Pomada)"])
        if tipo == "Serviço (Corte/Barba)":
            lista_itens = servicos_df["Nome do Serviço"].tolist()
            tabela_ref = servicos_df
            nome_col_preco = "Preço (R$)"
            categoria_venda = "Serviço"
        else:
            lista_itens = produtos_df["Nome do Produto"].tolist()
            tabela_ref = produtos_df
            nome_col_preco = "Preço de Venda"
            categoria_venda = "Produto"
            
        item_selecionado = st.selectbox("Selecione o Item:", lista_itens)
        qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1)
        
    with col2:
        forma_pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
        lista_barbeiros_sistema = barbeiros_df["Nome"].tolist() if not barbeiros_df.empty else ["G."]
        barbeiro_venda = st.selectbox("Barbeiro Profissional:", lista_barbeiros_sistema)
        cliente = st.text_input("Nome do Cliente (Opcional):", value="Avulso")
    
    preco_unitario = tabela_ref[tabela_ref.iloc[:, 1] == item_selecionado][nome_col_preco].values[0]
    valor_total = float(preco_unitario) * qtd
    
    st.write(f"### Valor Total do Lançamento: R$ {valor_total:.2f}")
    
    if st.button("Confirmar Lançamento", type="primary"):
        nova_venda = pd.DataFrame([{
            "Data": datetime.now().strftime("%Y-%m-%d"),
            "Item": item_selecionado,
            "Tipo": categoria_venda,
            "Quantidade": qtd,
            "Valor Total": valor_total,
            "Forma de Pagamento": forma_pagamento,
            "Barbeiro": barbeiro_venda,
            "Cliente": cliente
        }])
        vendas_df = pd.concat([vendas_df, nova_venda], ignore_index=True)
        vendas_df.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
        
        st.success(f"✅ SUCESSO! {categoria_venda} '{item_selecionado}' lançado por {barbeiro_venda}!")
        time.sleep(1.2)
        st.rerun()

# ---------------- MÓDULO 2: LANÇAR GASTO ----------------
elif menu == "📉 Lançar Gasto/Despesa" and st.session_state["perfil"] == "admin":
    st.header("Registrar Saída de Caixa / Gastos")
    col1, col2 = st.columns(2)
    with col1:
        descricao = st.text_input("Descrição do Gasto:")
        valor_gasto = st.number_input("Valor Pago (R$):", min_value=0.0, step=0.50)
    with col2:
        categoria = st.selectbox("Categoria:", ["Infraestrutura (Luz/Água/Aluguel)", "Produtos (Reposição de Estoque)", "Equipamentos/Ferramentas", "Outros"])
        
    if st.button("Salvar Despesa", type="primary"):
        if descricao != "" and valor_gasto > 0:
            novo_gasto = pd.DataFrame([{
                "Data": datetime.now().strftime("%Y-%m-%d"),
                "Descrição": descricao,
                "Valor (R$)": valor_gasto,
                "Categoria": categoria
            }])
            gastos_df = pd.concat([gastos_df, novo_gasto], ignore_index=True)
            gastos_df.to_csv(ARQUIVO_GASTOS, index=False, encoding='utf-8')
            
            st.success(f"✅ Gasto '{descricao}' registrado com sucesso!")
            time.sleep(1.2)
            st.rerun()
