import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuração da página da Barbearia
st.set_page_config(page_title="Barbearia - Controle de Estoque e Vendas", layout="wide")
st.title("💈 Sistema de Controle - Barbearia")

# Nome exato do arquivo com o espaço antes do ponto
EXCEL_FILE = "Sistema_Controle_Barbearia .xlsx"

# Função para carregar os dados do Excel de forma segura
def carregar_dados():
    if os.path.exists(EXCEL_FILE):
        try:
            xl = pd.ExcelFile(EXCEL_FILE)
            abas_existentes = xl.sheet_names
            
            # Encontrar os nomes das abas ignorando espaços em branco nas pontas
            aba_servicos = next((x for x in abas_existentes if x.strip() == "Serviços"), None)
            aba_produtos = next((x for x in abas_existentes if x.strip() == "Produtos"), None)
            aba_vendas = next((x for x in abas_existentes if x.strip() == "Vendas"), None)
            
            if not aba_servicos or not aba_produtos or not aba_vendas:
                st.error(f"Erro: Não encontramos todas as abas necessárias no Excel. As abas atuais são: {abas_existentes}")
                return None
                
            return {
                "Serviços": pd.read_excel(EXCEL_FILE, sheet_name=aba_servicos),
                "Produtos": pd.read_excel(EXCEL_FILE, sheet_name=aba_produtos),
                "Vendas": pd.read_excel(EXCEL_FILE, sheet_name=aba_vendas)
            }
        except Exception as e:
            st.error(f"Erro ao ler as abas do Excel: {e}")
            return None
    else:
        st.error(f"Arquivo Excel '{EXCEL_FILE}' não encontrado no GitHub!")
        return None

dados = carregar_dados()

if dados is not None:
    # Garantir que as colunas existam e sejam numéricas
    colunas_vendas = ["Data e Hora", "Item", "Tipo", "Quantidade", "Valor Total", "Forma de Pagamento"]
    for col in colunas_vendas:
        if col not in dados["Vendas"].columns:
            dados["Vendas"][col] = None
            
    dados["Vendas"]["Valor Total"] = pd.to_numeric(dados["Vendas"]["Valor Total"], errors='coerce').fillna(0)
    dados["Vendas"]["Quantidade"] = pd.to_numeric(dados["Vendas"]["Quantidade"], errors='coerce').fillna(0)

    # Menu Lateral do Sistema
    menu = st.sidebar.radio("Navegação", ["💸 Lançar Venda", "📦 Estoque & Serviços", "📊 Relatórios (Dashboard)", "⚙️ Configurações"])

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
            
            # Adicionar nova venda
            dados["Vendas"] = pd.concat([dados["Vendas"], nova_venda], ignore_index=True)
            
            # Salvar no Excel
            with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
                dados["Serviços"].to_excel(writer, sheet_name="Serviços", index=False)
                dados["Produtos"].to_excel(writer, sheet_name="Produtos", index=False)
                dados["Vendas"].to_excel(writer, sheet_name="Vendas", index=False)
                
            st.success(f"Sucesso! {item_selecionado} lançado. Atualizando sistema...")
            st.rerun()

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
        
        vendas_df = dados["Vendas"].dropna(subset=["Item"])
        
        if not vendas_df.empty:
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
            st.info("Nenhuma venda cadastrada ou histórico limpo. Faturamento atual: R$ 0,00")

    # ---------------- MÓDULO 4: CONFIGURAÇÕES (LIMPEZA) ----------------
    elif menu == "⚙️ Configurações":
        st.header("Configurações do Sistema")
        st.write("Use esta área para gerenciar os dados armazenados na planilha.")
        
        st.warning("Atenção: A ação abaixo vai apagar os testes antigos para começar do zero.")
        if st.button("⚠️ Limpar Todas as Vendas de Teste (Zerar Histórico)", type="primary"):
            dados["Vendas"] = pd.DataFrame(columns=colunas_vendas)
            
            with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
                dados["Serviços"].to_excel(writer, sheet_name="Serviços", index=False)
                dados["Produtos"].to_excel(writer, sheet_name="Produtos", index=False)
                dados["Vendas"].to_excel(writer, sheet_name="Vendas", index=False)
                
            st.success("Histórico limpo com sucesso! O seu faturamento foi zerado.")
            st.rerun()
