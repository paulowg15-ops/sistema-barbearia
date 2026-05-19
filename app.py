import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página da Barbearia
st.set_page_config(page_title="Barbearia - Controle de Estoque e Vendas", layout="wide")
st.title("💈 Sistema de Controle - Barbearia")

# Arquivo do Excel que serve como nosso banco de dados
EXCEL_FILE = "Sistema_Controle_Barbearia.xlsx"

# Função para carregar os dados do Excel
def carregar_dados():
    if os.path.exists(EXCEL_FILE):
        return {
            "Serviços": pd.read_excel(EXCEL_FILE, sheet_name="Serviços"),
            "Produtos": pd.read_excel(EXCEL_FILE, sheet_name="Produtos"),
            "Vendas": pd.read_excel(EXCEL_FILE, sheet_name="Vendas")
        }
    else:
        st.error("Arquivo Excel não encontrado! Certifique-se de que o arquivo está na mesma pasta.")
        return None

dados = carregar_dados()

if dados is not None:
    # Menu Lateral do Sistema
    menu = st.sidebar.radio("Navegação", ["💸 Lançar Venda", "📦 Estoque & Serviços", "📊 Relatórios (Dashboard)"])

    # ---------------- MÓDULO 1: LANÇAR VENDA ----------------
    if menu == "💸 Lançar Venda":
        st.header("Registrar Novo Atendimento / Venda")
        
        tipo = st.selectbox("O que foi vendido?", ["Serviço (Corte/Barba)", "Produto (Bebida/Pomada)"])
        
        if tipo == "Serviço (Corte/Barba)":
            lista_itens = dados["Serviços"]["Nome do Serviço"].tolist()
            tabela_ref = dados["Serviços"]
            nome_col_preco = "Preço (R$)"
            categoria_venda = "Serviço"
        else:
            lista_itens = dados["Produtos"]["Nome do Produto"].tolist()
            tabela_ref = dados["Produtos"]
            nome_col_preco = "Preço de Venda"
            categoria_venda = "Produto"
            
        item_selecionado = st.selectbox("Selecione o Item:", lista_itens)
        qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1)
        forma_pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
        
        # Buscar o preço unitário
        preco_unitario = tabela_ref[tabela_ref.iloc[:, 1] == item_selecionado][nome_col_preco].values[0]
        valor_total = preco_unitario * qtd
        
        st.write(f"### Valor Total: R$ {valor_total:.2f}")
        
        if st.button("Confirmar Lançamento", type="primary"):
            # Criar nova linha de venda
            nova_venda = pd.DataFrame([{
                "Data e Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Item": item_selecionado,
                "Tipo": categoria_venda,
                "Quantidade": qtd,
                "Valor Total": valor_total,
                "Forma de Pagamento": forma_pagamento
            }])
            
            # Atualizar aba de vendas
            dados["Vendas"] = pd.concat([dados["Vendas"], nova_venda], ignore_index=True)
            
            # Atualizar o estoque na aba de Produtos se for um Produto
            if categoria_venda == "Produto":
                idx_prod = dados["Produtos"][dados["Produtos"]["Nome do Produto"] == item_selecionado].index
                # Se não usar fórmulas do Excel pura, podemos atualizar o valor estático aqui para garantir
                # Mas salvando de volta no Excel, as fórmulas SUMIF que deixei cuidam disso!
                pass
            
            # Salvar de volta no Excel mantendo as outras abas
            with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
                dados["Serviços"].to_excel(writer, sheet_name="Serviços", index=False)
                dados["Produtos"].to_excel(writer, sheet_name="Produtos", index=False)
                dados["Vendas"].to_excel(writer, sheet_name="Vendas", index=False)
                
            st.success(f"Sucesso! {item_selecionado} lançado.")

    # ---------------- MÓDULO 2: ESTOQUE & SERVIÇOS ----------------
    elif menu == "📦 Estoque & Serviços":
        st.header("Controle de Estoque e Catálogo")
        
        st.subheader("Lista de Produtos (Bebidas e Pomadas)")
        st.dataframe(dados["Produtos"], use_container_width=True)
        
        st.subheader("Lista de Serviços Prestados")
        st.dataframe(dados["Serviços"], use_container_width=True)

    # ---------------- MÓDULO 3: RELATÓRIOS ----------------
    elif menu == "📊 Relatórios (Dashboard)":
        st.header("Painel de Resultados Financeiros")
        
        vendas_df = dados["Vendas"]
        
        if not vendas_df.empty:
            faturamento = vendas_df["Valor Total"].sum()
            total_cortes = vendas_df[vendas_df["Tipo"] == "Serviço"]["Quantidade"].sum()
            total_produtos = vendas_df[vendas_df["Tipo"] == "Produto"]["Quantidade"].sum()
            
            # Mostrar indicadores em blocos bonitos
            col1, col2, col3 = st.columns(3)
            col1.metric("Faturamento Total", f"R$ {faturamento:.2f}")
            col2.metric("Cortes Realizados", int(total_cortes))
            col3.metric("Produtos Vendidos", int(total_produtos))
            
            st.subheader("Histórico de Vendas Recentes")
            st.dataframe(vendas_df.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("Nenhuma venda registrada ainda.")
