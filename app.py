import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página da Barbearia
st.set_page_config(page_title="Barbearia - Sistema Avançado", layout="wide")

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
            # Validação dos dois usuários e senhas
            if usuario == "admin" and senha == "barba123":
                st.session_state["autenticado"] = True
                st.session_state["perfil"] = "admin"
                st.success("Acesso Admin liberado!")
                st.rerun()
            elif usuario == "barbeiro" and senha == "corte123":
                st.session_state["autenticado"] = True
                st.session_state["perfil"] = "barbeiro"
                st.success("Acesso Barbeiro liberado!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos!")
    st.stop()

# --- SE O USUÁRIO PASSAR DO LOGIN, O SISTEMA COMEÇA AQUI ---

st.title("💈 Sistema de Gestão Profissional - Barbearia")

# Bancos de dados em formato CSV
ARQUIVO_SERVICOS = "servicos.csv"
ARQUIVO_PRODUTOS = "produtos.csv"
ARQUIVO_VENDAS = "vendas.csv"
ARQUIVO_GASTOS = "gastos.csv"

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
            {"ID": 1, "Nome do Produto": "Pomada Modeladora", "Preço de Venda": 40.0, "Preço de Custo": 20.0, "Estoque Inicial": 10},
            {"ID": 2, "Nome do Produto": "Cerveja Long Neck", "Preço de Venda": 8.0, "Preço de Custo": 4.0, "Estoque Inicial": 24},
            {"ID": 3, "Nome do Produto": "Refrigerante Lata", "Preço de Venda": 5.0, "Preço de Custo": 2.5, "Estoque Inicial": 24},
            {"ID": 4, "Nome do Produto": "Água Mineral", "Preço de Venda": 3.0, "Preço de Custo": 1.0, "Estoque Inicial": 10},
            {"ID": 5, "Nome do Produto": "Óleo para Barba", "Preço de Venda": 35.0, "Preço de Custo": 18.0, "Estoque Inicial": 5}
        ]).to_csv(ARQUIVO_PRODUTOS, index=False, encoding='utf-8')

    if not os.path.exists(ARQUIVO_VENDAS):
        pd.DataFrame(columns=["Data", "Item", "Tipo", "Quantidade", "Valor Total", "Forma de Pagamento", "Barbeiro", "Cliente"]).to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')

    if not os.path.exists(ARQUIVO_GASTOS):
        pd.DataFrame(columns=["Data", "Descrição", "Valor (R$)", "Categoria"]).to_csv(ARQUIVO_GASTOS, index=False, encoding='utf-8')

inicializar_banco_de_dados()

servicos_df = pd.read_csv(ARQUIVO_SERVICOS, encoding='utf-8')
produtos_df = pd.read_csv(ARQUIVO_PRODUTOS, encoding='utf-8')
vendas_df = pd.read_csv(ARQUIVO_VENDAS, encoding='utf-8')
gastos_df = pd.read_csv(ARQUIVO_GASTOS, encoding='utf-8')

# --- CONTROLE DE MENUS POR PERFIL ---
if st.session_state["perfil"] == "admin":
    opcoes_menu = ["💸 Lançar Venda", "📉 Lançar Gasto/Despesa", "📦 Estoque & Serviços", "📊 Painel de Relatórios", "⚙️ Configurações"]
else:
    # O barbeiro só enxerga estas duas abas
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
        barbeiro_venda = st.text_input("Nome do Barbeiro:", value="G.")
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
        st.success(f"Venda de {item_selecionado} registrada com sucesso!")
        st.rerun()

# ---------------- MÓDULO 2: LANÇAR GASTO (APENAS ADMIN) ----------------
elif menu == "📉 Lançar Gasto/Despesa" and st.session_state["perfil"] == "admin":
    st.header("Registrar Saída de Caixa / Gastos")
    
    col1, col2 = st.columns(2)
    with col1:
        descricao = st.text_input("Descrição do Gasto (Ex: Conta de Luz, Compra de Cerveja):")
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
            st.success("Gasto registrado com sucesso!")
            st.rerun()
        else:
            st.error("Preencha a descrição e o valor corretamente.")

# ---------------- MÓDULO 3: ESTOQUE ----------------
elif menu == "📦 Estoque & Serviços":
    st.header("Controle de Estoque e Catálogo")
    
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    produtos_calculados = produtos_df.copy()
    qtd_vendida_map = vendas_df[vendas_df["Tipo"] == "Produto"].groupby("Item")["Quantidade"].sum().to_dict()
    
    produtos_calculados["Quantidade Vendida"] = produtos_calculados["Nome do Produto"].map(qtd_vendida_map).fillna(0).astype(int)
    produtos_calculados["Estoque Atual"] = produtos_calculados["Estoque Inicial"] - produtos_calculados["Quantidade Vendida"]
    
    st.subheader("📦 Lista de Produtos (Bebidas e Pomadas)")
    st.dataframe(produtos_calculados, use_container_width=True)
    
    st.subheader("💈 Lista de Serviços Prestados")
    st.dataframe(servicos_df, use_container_width=True)

# ---------------- MÓDULO 4: PAINEL DE RELATÓRIOS (APENAS ADMIN) ----------------
elif menu == "📊 Painel de Relatórios" and st.session_state["perfil"] == "admin":
    st.header("Painel Estatístico e Financeiro")
    
    vendas_df["Valor Total"] = pd.to_numeric(vendas_df["Valor Total"], errors='coerce').fillna(0)
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    gastos_df["Valor (R$)"] = pd.to_numeric(gastos_df["Valor (R$)"], errors='coerce').fillna(0)
    
    faturamento = vendas_df["Valor Total"].sum()
    total_gastos = gastos_df["Valor (R$)"].sum()
    lucro_liquido = faturamento - total_gastos
    
    total_cortes = vendas_df[vendas_df["Tipo"] == "Serviço"]["Quantidade"].sum()
    total_produtos = vendas_df[vendas_df["Tipo"] == "Produto"]["Quantidade"].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento Bruto", f"R$ {faturamento:.2f}")
    col2.metric("Total de Gastos", f"R$ {total_gastos:.2f}", delta=f"-R$ {total_gastos:.2f}", delta_color="inverse")
    col3.metric("Lucro Líquido Real", f"R$ {lucro_liquido:.2f}", delta=f"R$ {lucro_liquido:.2f}")
    
    st.markdown("---")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("📅 Faturamento Diário")
        if not vendas_df.empty:
            faturamento_diario = vendas_df.groupby("Data")["Valor Total"].sum()
            st.line_chart(faturamento_diario)
        else:
            st.info("Sem dados de vendas para gerar o gráfico.")
            
    with col_g2:
        st.subheader("💰 Divisão de Receitas (Tipo)")
        if not vendas_df.empty:
            divisao_tipo = vendas_df.groupby("Tipo")["Valor Total"].sum()
            st.bar_chart(divisao_tipo)
        else:
            st.info("Sem dados de vendas para gerar o gráfico.")

    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📋 Histórico de Vendas", "📉 Histórico de Gastos"])
    with tab1:
        st.dataframe(vendas_df.sort_index(ascending=False), use_container_width=True)
    with tab2:
        st.dataframe(gastos_df.sort_index(ascending=False), use_container_width=True)

# ---------------- MÓDULO 5: CONFIGURAÇÕES (APENAS ADMIN) ----------------
elif menu == "⚙️ Configurações" and st.session_state["perfil"] == "admin":
    st.header("Configurações Globais do Sistema")
    
    st.warning("Ações de Limpeza de Dados (Não podem ser desfeitas!)")
    
    if st.button("⚠️ Limpar Histórico de Vendas", type="primary"):
        pd.DataFrame(columns=["Data", "Item", "Tipo", "Quantidade", "Valor Total", "Forma de Pagamento", "Barbeiro", "Cliente"]).to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
        st.success("Histórico de vendas zerado!")
        st.rerun()
        
    if st.button("⚠️ Limpar Histórico de Gastos"):
        pd.DataFrame(columns=["Data", "Descrição", "Valor (R$)", "Categoria"]).to_csv(ARQUIVO_GASTOS, index=False, encoding='utf-8')
        st.success("Histórico de despesas zerado!")
        st.rerun()
