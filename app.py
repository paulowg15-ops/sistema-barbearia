import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página da Barbearia
st.set_page_config(page_title="Barbearia - Controle de Estoque e Vendas", layout="wide")
st.title("💈 Sistema de Controle - Barbearia")

# Arquivos de texto simples para armazenar os dados (Sem risco de dar erro)
ARQUIVO_SERVICOS = "servicos.csv"
ARQUIVO_PRODUTOS = "produtos.csv"
ARQUIVO_VENDAS = "vendas.csv"

# Função para garantir que os bancos de dados existam com os dados padrão
def inicializar_banco_de_dados():
    # 1. Inicializar Serviços se não existir
    if not os.path.exists(ARQUIVO_SERVICOS):
        df_servicos = pd.DataFrame([
            {"ID": 1, "Nome do Serviço": "Corte Social", "Preço (R$)": 35.0},
            {"ID": 2, "Nome do Serviço": "Barba Completa", "Preço (R$)": 25.0},
            {"ID": 3, "Nome do Serviço": "Combo (Corte + Barba)", "Preço (R$)": 55.0},
            {"ID": 4, "Nome do Serviço": "Acabamento / Pezinho", "Preço (R$)": 15.0},
            {"ID": 5, "Nome do Serviço": "Platinado / Nevou", "Preço (R$)": 80.0}
        ])
        df_servicos.to_csv(ARQUIVO_SERVICOS, index=False, encoding='utf-8')

    # 2. Inicializar Produtos se não existir
    if not os.path.exists(ARQUIVO_PRODUTOS):
        df_produtos = pd.DataFrame([
            {"ID": 1, "Nome do Produto": "Pomada Modeladora", "Preço de Venda": 40.0, "Preço de Custo": 20.0, "Estoque Inicial": 10},
            {"ID": 2, "Nome do Produto": "Cerveja Long Neck", "Preço de Venda": 8.0, "Preço de Custo": 4.0, "Estoque Inicial": 24},
            {"ID": 3, "Nome do Produto": "Refrigerante Lata", "Preço de Venda": 5.0, "Preço de Custo": 2.5, "Estoque Inicial": 24},
            {"ID": 4, "Nome do Produto": "Água Mineral", "Preço de Venda": 3.0, "Preço de Custo": 1.0, "Estoque Inicial": 10},
            {"ID": 5, "Nome do Produto": "Óleo para Barba", "Preço de Venda": 35.0, "Preço de Custo": 18.0, "Estoque Inicial": 5}
        ])
        df_produtos.to_csv(ARQUIVO_PRODUTOS, index=False, encoding='utf-8')

    # 3. Inicializar Vendas se não existir
    if not os.path.exists(ARQUIVO_VENDAS):
        colunas_vendas = ["Data e Hora", "Item", "Tipo", "Quantidade", "Valor Total", "Forma de Pagamento"]
        df_vendas = pd.DataFrame(columns=colunas_vendas)
        df_vendas.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')

# Inicializa as tabelas automaticamente nos servidores do Streamlit
inicializar_banco_de_dados()

# Carregar os dados
servicos_df = pd.read_csv(ARQUIVO_SERVICOS, encoding='utf-8')
produtos_df = pd.read_csv(ARQUIVO_PRODUTOS, encoding='utf-8')
vendas_df = pd.read_csv(ARQUIVO_VENDAS, encoding='utf-8')

# Menu Lateral do Sistema
menu = st.sidebar.radio("Navegação", ["💸 Lançar Venda", "📦 Estoque & Serviços", "📊 Relatórios (Dashboard)", "⚙️ Configurações"])

# ---------------- MÓDULO 1: LANÇAR VENDA ----------------
if menu == "💸 Lançar Venda":
    st.header("Registrar Novo Atendimento / Venda")
    
    tipo = st.selectbox("O que foi vendido?", ["Serviço (Corte/Barba)", "Produto (Bebida/Pomada)"])
    
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
    forma_pagamento = st.selectbox("Forma de Pagamento:", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
    
    # Buscar o preço unitário
    preco_unitario = tabela_ref[tabela_ref.iloc[:, 1] == item_selecionado][nome_col_preco].values[0]
    valor_total = float(preco_unitario) * qtd
    
    st.write(f"### Valor Total: R$ {valor_total:.2f}")
    
    if st.button("Confirmar Lançamento", type="primary"):
        nova_venda = pd.DataFrame([{
            "Data e Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Item": item_selecionado,
            "Tipo": categoria_venda,
            "Quantidade": qtd,
            "Valor Total": valor_total,
            "Forma de Pagamento": forma_pagamento
        }])
        
        # Unir e salvar novas vendas
        vendas_df = pd.concat([vendas_df, nova_venda], ignore_index=True)
        vendas_df.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
            
        st.success(f"Sucesso! {item_selecionado} lançado.")
        st.rerun()

# ---------------- MÓDULO 2: ESTOQUE & SERVIÇOS ----------------
elif menu == "📦 Estoque & Serviços":
    st.header("Controle de Estoque e Catálogo")
    
    st.subheader("Lista de Produtos (Bebidas e Pomadas)")
    
    # Calcular estoque dinamicamente: Estoque Atual = Inicial - Quantidade Vendida
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    produtos_calculados = produtos_df.copy()
    
    qtd_vendida_map = vendas_df[vendas_df["Tipo"] == "Produto"].groupby("Item")["Quantidade"].sum().to_dict()
    
    produtos_calculados["Quantidade Vendida"] = produtos_calculados["Nome do Produto"].map(qtd_vendida_map).fillna(0).astype(int)
    produtos_calculados["Estoque Atual"] = produtos_calculados["Estoque Inicial"] - produtos_calculados["Quantidade Vendida"]
    
    st.dataframe(produtos_calculados, use_container_width=True)
    
    st.subheader("Lista de Serviços Prestados")
    st.dataframe(servicos_df, use_container_width=True)

# ---------------- MÓDULO 3: RELATÓRIOS ----------------
elif menu == "📊 Relatórios (Dashboard)":
    st.header("Painel de Resultados Financeiros")
    
    if not vendas_df.empty:
        vendas_df["Valor Total"] = pd.to_numeric(vendas_df["Valor Total"], errors='coerce').fillna(0)
        vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
        
        faturamento = vendas_df["Valor Total"].sum()
        total_cortes = vendas_df[vendas_df["Tipo"] == "Serviço"]["Quantidade"].sum()
        total_produtos = vendas_df[vendas_df["Tipo"] == "Produto"]["Quantidade"].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Faturamento Total", f"R$ {faturamento:.2f}")
        col2.metric("Cortes Realizados", int(total_cortes))
        col3.metric("Produtos Vendidos", int(total_produtos))
        
        st.subheader("Histórico de Vendas Recentes")
        st.dataframe(vendas_df.sort_index(ascending=False), use_container_width=True)
    else:
        st.info("Nenhum lançamento ativo encontrado. Faturamento atual: R$ 0,00")

# ---------------- MÓDULO 4: CONFIGURAÇÕES (LIMPEZA) ----------------
elif menu == "⚙️ Configurações":
    st.header("Configurações do Sistema")
    st.write("Use esta área para resetar o histórico do seu aplicativo.")
    
    st.warning("Atenção: A ação abaixo vai apagar o histórico de lançamentos para começar do zero.")
    if st.button("⚠️ Limpar Tudo e Iniciar do Zero (Faturamento R$ 0,00)", type="primary"):
        df_vendas_vazia = pd.DataFrame(columns=["Data e Hora", "Item", "Tipo", "Quantidade", "Valor Total", "Forma de Pagamento"])
        df_vendas_vazia.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
        st.success("Histórico limpo com sucesso!")
        st.rerun()
