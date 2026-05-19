import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página da Barbearia
st.set_page_config(page_title="Barbearia - Sistema Avançado", layout="wide")
st.title("💈 Sistema de Gestão Profissional - Barbearia")

# Bancos de dados em formato CSV
ARQUIVO_SERVICOS = "servicos.csv"
ARQUIVO_PRODUTOS = "produtos.csv"
ARQUIVO_VENDAS = "vendas.csv"
ARQUIVO_GASTOS = "gastos.csv"

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

# Inicializar os arquivos
inicializar_banco_de_dados()

# Carregar os dados atuais
servicos_df = pd.read_csv(ARQUIVO_SERVICOS, encoding='utf-8')
produtos_df = pd.read_csv(ARQUIVO_PRODUTOS, encoding='utf-8')
vendas_df = pd.read_csv(ARQUIVO_VENDAS, encoding='utf-8')
gastos_df = pd.read_csv(ARQUIVO_GASTOS, encoding='utf-8')

# Menu Lateral Avançado
menu = st.sidebar.radio("Navegação", [
    "💸 Lançar Venda", 
    "📉 Lançar Gasto/Despesa", 
    "📦 Estoque & Serviços", 
    "📊 Painel de Relatórios", 
    "⚙️ Configurações"
])

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
        barbeiro = st.text_input("Nome do Barbeiro:", value="G.")
        cliente = st.text_input("Nome do Cliente (Opcional):", value="Avulso")
    
    # Buscar preço
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
            "Barbeiro": barbeiro,
            "Cliente": cliente
        }])
        vendas_df = pd.concat([vendas_df, nova_venda], ignore_index=True)
        vendas_df.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
        st.success(f"Venda de {item_selecionado} registada com sucesso!")
        st.rerun()

# ---------------- MÓDULO 2: LANÇAR GASTO ----------------
elif menu == "📉 Lançar Gasto/Despesa":
    st.header("Registrar Saída de Caixa / Gastos")
    
    col1, col2 = st.columns(2)
    with col1:
        descricao = st.text_input("Descrição do Gasto (Ex: Conta de Luz, Compra de Cerveja):")
        valor_gasto = st.number_input("Valor Pago (R$):", min_value=0.0, step=0.50)
    with col2:
        categoria = st.selectbox("Categoria:", ["Infraestrutura (Luz/Água/Aluguer)", "Produtos (Reposição de Estoque)", "Equipamentos/Ferramentas", "Outros"])
        
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
            st.success("Gasto registado com sucesso!")
            st.rerun()
        else:
            st.error("Preencha a descrição e o valor corretamente.")

# ---------------- MÓDULO 3: ESTOQUE ----------------
elif menu == "📦 Estoque & Serviços":
    st.header("Controle de Estoque e Catálogo")
    
    # Calcular estoque
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    produtos_calculados = produtos_df.copy()
    qtd_vendida_map = vendas_df[vendas_df["Tipo"] == "Produto"].groupby("Item")["Quantidade"].sum().to_dict()
    
    produtos_calculados["Quantidade Vendida"] = produtos_calculados["Nome do Produto"].map(qtd_vendida_map).fillna(0).astype(int)
    produtos_calculados["Estoque Atual"] = produtos_calculados["Estoque Inicial"] - produtos_calculados["Quantidade Vendida"]
    
    st.subheader("📦 Lista de Produtos (Bebidas e Pomadas)")
    st.dataframe(produtos_calculados, use_container_width=True)
    
    st.subheader("💈 Lista de Serviços Prestados")
    st.dataframe(servicos_df, use_container_width=True)

# ---------------- MÓDULO 4: PAINEL DE RELATÓRIOS ----------------
elif menu == "📊 Painel de Relatórios":
    st.header("Painel Estatístico e Financeiro")
    
    # Garantir dados numéricos
    vendas_df["Valor Total"] = pd.to_numeric(vendas_df["Valor Total"], errors='coerce').fillna(0)
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    gastos_df["Valor (R$)"] = pd.to_numeric(gastos_df["Valor (R$)"], errors='coerce').fillna(0)
    
    # Cálculos
    faturamento = vendas_df["Valor Total"].sum()
    total_gastos = gastos_df["Valor (R$)"].sum()
    lucro_liquido = faturamento - total_gastos
    
    total_cortes = vendas_df[vendas_df["Tipo"] == "Serviço"]["Quantidade"].sum()
    total_produtos = vendas_df[vendas_df["Tipo"] == "Produto"]["Quantidade"].sum()
    
    # Blocos de Indicadores Financeiros
    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento Bruto", f"R$ {faturamento:.2f}")
    col2.metric("Total de Gastos", f"R$ {total_gastos:.2f}", delta=f"-R$ {total_gastos:.2f}", delta_color="inverse")
    col3.metric("Lucro Líquido Real", f"R$ {lucro_liquido:.2f}", delta=f"R$ {lucro_liquido:.2f}")
    
    st.markdown("---")
    
    # ÁREA DE GRÁFICOS VISUAIS
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
    
    # Tabelas de Histórico
    tab1, tab2 = st.tabs(["📋 Histórico de Vendas", "📉 Histórico de Gastos"])
    with tab1:
        st.dataframe(vendas_df.sort_index(ascending=False), use_container_width=True)
    with tab2:
        st.dataframe(gastos_df.sort_index(ascending=False), use_container_width=True)

# ---------------- MÓDULO
