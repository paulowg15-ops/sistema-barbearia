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
        # Adicionada a coluna 'Comissão Barbeiro (R$)' com valor padrão de 0.0
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
# Garantir que a coluna de comissão exista caso o arquivo já tenha sido criado antes
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

# ---------------- MÓDULO 3: GERENCIAR BARBEIROS (CADASTRO E EXCLUSÃO) ----------------
elif menu == "👥 Cadastrar Barbeiro" and st.session_state["perfil"] == "admin":
    st.header("Gerenciamento de Barbeiros da Equipe")
    
    col_cad1, col_cad2 = st.columns(2)
    with col_cad1:
        st.subheader("➕ Adicionar Profissional")
        novo_nome = st.text_input("Nome do Profissional:")
        nova_comissao = st.number_input("Porcentagem de Comissão nos Serviços (%):", min_value=0.0, max_value=100.0, value=50.0, step=5.0)
        
        if st.button("Cadastrar Barbeiro", type="primary"):
            if novo_nome != "" and novo_nome not in barbeiros_df["Nome"].tolist():
                novo_b = pd.DataFrame([{"Nome": novo_nome, "Comissão (%)": nova_comissao}])
                barbeiros_df = pd.concat([barbeiros_df, novo_b], ignore_index=True)
                barbeiros_df.to_csv(ARQUIVO_BARBEIROS, index=False, encoding='utf-8')
                
                st.success(f"👤 Profissional '{novo_nome}' adicionado com sucesso!")
                time.sleep(1.2)
                st.rerun()
            else:
                st.error("Nome inválido ou barbeiro já cadastrado.")
                
        st.markdown("---")
        st.subheader("❌ Remover Profissional")
        if not barbeiros_df.empty:
            barbeiro_remover = st.selectbox("Selecione o Barbeiro para Excluir:", barbeiros_df["Nome"].tolist())
            if st.button("Remover do Sistema", type="secondary"):
                barbeiros_df = barbeiros_df[barbeiros_df["Nome"] != barbeiro_remover]
                barbeiros_df.to_csv(ARQUIVO_BARBEIROS, index=False, encoding='utf-8')
                st.success(f"🗑️ Barbeiro '{barbeiro_remover}' foi excluído do sistema.")
                time.sleep(1.2)
                st.rerun()
        else:
            st.info("Nenhum barbeiro cadastrado.")
                
    with col_cad2:
        st.subheader("👥 Profissionais Ativos Atualmente")
        st.dataframe(barbeiros_df, use_container_width=True)

# ---------------- MÓDULO 4: ESTOQUE & SERVIÇOS ----------------
elif menu == "📦 Estoque & Serviços":
    st.header("Controle de Estoque e Catálogo")
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    produtos_calculados = produtos_df.copy()
    qtd_vendida_map = vendas_df[vendas_df["Tipo"] == "Produto"].groupby("Item")["Quantidade"].sum().to_dict()
    
    produtos_calculados["Quantidade Vendida"] = produtos_calculados["Nome do Produto"].map(qtd_vendida_map).fillna(0).astype(int)
    produtos_calculados["Estoque Atual"] = produtos_calculados["Estoque Inicial"] - produtos_calculados["Quantidade Vendida"]
    
    st.subheader("📦 Lista de Produtos e Comissões fixas")
    st.dataframe(produtos_calculados, use_container_width=True)
    
    st.subheader("💈 Lista de Serviços Prestados")
    st.dataframe(servicos_df, use_container_width=True)

# ---------------- MÓDULO 5: GERENCIAR CATÁLOGO (PREÇOS E COMISSÃO DE PRODUTOS) ----------------
elif menu == "⚙️ Gerenciar Catálogo" and st.session_state["perfil"] == "admin":
    st.header("⚙️ Configurar Catálogo (Serviços e Produtos)")
    aba_serv, aba_prod = st.tabs(["💈 Serviços", "📦 Produtos"])
    
    with aba_serv:
        st.subheader("Adicionar Novo Serviço")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            s_nome = st.text_input("Nome do Novo Serviço:")
        with col_s2:
            s_preco = st.number_input("Preço Cobrado (R$):", min_value=0.0, value=20.0, step=5.0)
            
        if st.button("Adicionar Serviço"):
            if s_nome != "":
                novo_id = int(servicos_df["ID"].max() + 1) if not servicos_df.empty else 1
                novo_s = pd.DataFrame([{"ID": novo_id, "Nome do Serviço": s_nome, "Preço (R$)": s_preco}])
                servicos_df = pd.concat([servicos_df, novo_s], ignore_index=True)
                servicos_df.to_csv(ARQUIVO_SERVICOS, index=False, encoding='utf-8')
                st.success(f"✨ Novo serviço '{s_nome}' incluído!")
                time.sleep(1.2)
                st.rerun()
                
        st.markdown("---")
        st.subheader("Editar Preço de Serviço Existente")
        servico_editar = st.selectbox("Escolha o Serviço para Editar:", servicos_df["Nome do Serviço"].tolist())
        novo_preco_s = st.number_input("Novo Preço (R$):", min_value=0.0, value=float(servicos_df[servicos_df["Nome do Serviço"] == servico_editar]["Preço (R$)"].values[0]))
        
        if st.button("Salvar Novo Preço"):
            servicos_df.loc[servicos_df["Nome do Serviço"] == servico_editar, "Preço (R$)"] = novo_preco_s
            servicos_df.to_csv(ARQUIVO_SERVICOS, index=False, encoding='utf-8')
            st.success("🎉 Preço atualizado com sucesso!")
            time.sleep(1.2)
            st.rerun()

    with aba_prod:
        st.subheader("Adicionar Novo Produto / Bebida")
        col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
        with col_p1:
            p_nome = st.text_input("Nome do Produto:")
        with col_p2:
            p_venda = st.number_input("Preço Venda (R$):", min_value=0.0, value=10.0)
        with col_p3:
            p_custo = st.number_input("Preço Custo (R$):", min_value=0.0, value=5.0)
        with col_p4:
            p_estoque = st.number_input("Estoque Inicial:", min_value=0, value=10)
        with col_p5:
            p_comis = st.number_input("Comissão do Barbeiro (R$):", min_value=0.0, value=0.0, description="Valor fixo por venda")
            
        if st.button("Adicionar Produto"):
            if p_nome != "":
                novo_id = int(produtos_df["ID"].max() + 1) if not produtos_df.empty else 1
                novo_p = pd.DataFrame([{"ID": novo_id, "Nome do Produto": p_nome, "Preço de Venda": p_venda, "Preço de Custo": p_custo, "Estoque Inicial": p_estoque, "Comissão Barbeiro (R$)": p_comis}])
                produtos_df = pd.concat([produtos_df, novo_p], ignore_index=True)
                produtos_df.to_csv(ARQUIVO_PRODUTOS, index=False, encoding='utf-8')
                st.success(f"📦 Produto '{p_nome}' cadastrado!")
                time.sleep(1.2)
                st.rerun()
                
        st.markdown("---")
        st.subheader("Editar Produto e Comissão Existente")
        prod_editar = st.selectbox("Escolha o Produto para Modificar:", produtos_df["Nome do Produto"].tolist())
        
        col_ed1, col_ed2, col_ed3, col_ed4 = st.columns(4)
        item_linha = produtos_df[produtos_df["Nome do Produto"] == prod_editar]
        with col_ed1:
            ed_venda = st.number_input("Mudar Preço Venda:", value=float(item_linha["Preço de Venda"].values[0]))
        with col_ed2:
            ed_custo = st.number_input("Mudar Preço Custo:", value=float(item_linha["Preço de Custo"].values[0]))
        with col_ed3:
            ed_estoque = st.number_input("Mudar Estoque Inicial:", value=int(item_linha["Estoque Inicial"].values[0]))
        with col_ed4:
            ed_comis = st.number_input("Mudar Comissão Barbeiro (R$):", value=float(item_linha["Comissão Barbeiro (R$)"].values[0]))
            
        if st.button("Salvar Modificações do Produto"):
            produtos_df.loc[produtos_df["Nome do Produto"] == prod_editar, ["Preço de Venda", "Preço de Custo", "Estoque Inicial", "Comissão Barbeiro (R$)"]] = [ed_venda, ed_custo, ed_estoque, ed_comis]
            produtos_df.to_csv(ARQUIVO_PRODUTOS, index=False, encoding='utf-8')
            st.success("🔥 Produto e Valor de Comissão atualizados com sucesso!")
            time.sleep(1.2)
            st.rerun()

# ---------------- MÓDULO 6: PAINEL DE RELATÓRIOS (ATUALIZADO COM COMISSÃO DE PRODUTO) ----------------
elif menu == "📊 Painel de Relatórios" and st.session_state["perfil"] == "admin":
    st.header("Painel Estatístico, Financeiro e Comissões Integradas")
    
    vendas_df["Valor Total"] = pd.to_numeric(vendas_df["Valor Total"], errors='coerce').fillna(0)
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    gastos_df["Valor (R$)"] = pd.to_numeric(gastos_df["Valor (R$)"], errors='coerce').fillna(0)
    
    faturamento = vendas_df["Valor Total"].sum()
    total_gastos = gastos_df["Valor (R$)"].sum()
    lucro_liquido = faturamento - total_gastos
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento Bruto", f"R$ {faturamento:.2f}")
    col2.metric("Total de Gastos", f"R$ {total_gastos:.2f}", delta=f"-R$ {total_gastos:.2f}", delta_color="inverse")
    col3.metric("Lucro Líquido Real", f"R$ {lucro_liquido:.2f}")
    
    st.markdown("---")
    st.subheader("💸 Relatório Unificado de Comissões Semanais por Barbeiro")
    
    if not barbeiros_df.empty:
        relatorio_comissao = []
        
        # Mapeamento rápido de comissão por produto em dinheiro
        mapa_comissao_produto = produtos_df.set_index("Nome do Produto")["Comissão Barbeiro (R$)"].to_dict()
        
        for _, b in barbeiros_df.iterrows():
            nome_b = b["Nome"]
            porcentagem_servico = b["Comissão (%)"]
            
            # Filtrar vendas deste barbeiro
            vendas_do_barbeiro = vendas_df[vendas_df["Barbeiro"] == nome_b]
            
            # 1. Cálculo de Serviços (Porcentagem)
            servicos_b = vendas_do_barbeiro[vendas_do_barbeiro["Tipo"] == "Serviço"]
            faturamento_servicos = servicos_b["Valor Total"].sum()
            total_cortes = servicos_b["Quantidade"].sum()
            valor_comissao_servico = faturamento_servicos * (porcentagem_servico / 100.0)
            
            # 2. Cálculo de Produtos (Valor Fixo por Item)
            produtos_b = vendas_do_barbeiro[vendas_do_barbeiro["Tipo"] == "Produto"]
            valor_comissao_produto = 0.0
            total_produtos_vendidos = produtos_b["Quantidade"].sum()
            
            for _, venda_p in produtos_b.iterrows():
                nome_p = venda_p["Item"]
                qtd_p = venda_p["Quantidade"]
                comissao_unitaria_p = mapa_comissao_produto.get(nome_p, 0.0)
                valor_comissao_produto += float(comissao_unitaria_p) * float(qtd_p)
                
            # Total Geral a pagar
            total_geral_a_pagar = valor_comissao_servico + valor_comissao_produto
            
            relatorio_comissao.append({
                "Barbeiro": nome_b,
                "Qtd Serviços": int(total_cortes),
                "Comissão Serviços": f"R$ {valor_comissao_servico:.2f} ({int(porcentagem_servico)}%)",
                "Qtd Produtos": int(total_produtos_vendidos),
                "Comissão Produtos": f"R$ {valor_comissao_produto:.2f}",
                "TOTAL A PAGAR (R$)": f"R$ {total_geral_a_pagar:.2f}"
            })
            
        st.dataframe(pd.DataFrame(relatorio_comissao), use_container_width=True)
    else:
        st.info("Nenhum barbeiro ativo cadastrado.")
        
    st.markdown("---")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("📅 Faturamento Diário")
        if not vendas_df.empty:
            st.line_chart(vendas_df.groupby("Data")["Valor Total"].sum())
    with col_g2:
        st.subheader("💰 Divisão de Receitas")
        if not vendas_df.empty:
            st.bar_chart(vendas_df.groupby("Tipo")["Valor Total"].sum())

    st.markdown("---")
    tab1, tab2 = st.tabs(["📋 Histórico de Vendas", "📉 Histórico de Gastos"])
    with tab1:
        st.dataframe(vendas_df.sort_index(ascending=False), use_container_width=True)
    with tab2:
        st.dataframe(gastos_df.sort_index(ascending=False), use_container_width=True)

# ---------------- MÓDULO 7: CONFIGURAÇÕES ----------------
elif menu == "⚙️ Configurações" and st.session_state["perfil"] == "admin":
    st.header("Configurações Globais")
    st.warning("Ações de Limpeza de Dados (Não podem ser desfeitas!)")
    
    if st.button("⚠️ Limpar Histórico de Vendas", type="primary"):
        pd.DataFrame(columns=["Data", "Item", "Tipo", "Quantidade", "Valor Total", "Forma de Pagamento", "Barbeiro", "Cliente"]).to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
        st.success("Histórico zerado!")
        st.rerun()
