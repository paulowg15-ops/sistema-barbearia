import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time

# Configuração da página da Barbearia com layout responsivo
st.set_page_config(page_title="Barbearia - Sistema Premium", layout="wide", initial_sidebar_state="expanded")

# Bancos de dados em formato CSV
ARQUIVO_SERVICOS = "servicos.csv"
ARQUIVO_PRODUTOS = "produtos.csv"
ARQUIVO_VENDAS = "vendas.csv"
ARQUIVO_GASTOS = "gastos.csv"
ARQUIVO_BARBEIROS = "barbeiros.csv"
ARQUIVO_ASSINATURAS = "assinaturas.csv"
ARQUIVO_PRESENCAS = "presencas.csv"

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
        pd.DataFrame([{"Nome": "G.", "Comissão (%)": 50.0}]).to_csv(ARQUIVO_BARBEIROS, index=False, encoding='utf-8')

    if not os.path.exists(ARQUIVO_ASSINATURAS):
        pd.DataFrame(columns=["Cliente", "Plano", "Data Inicio", "Data Vencimento", "Valor Mensal"]).to_csv(ARQUIVO_ASSINATURAS, index=False, encoding='utf-8')

    if not os.path.exists(ARQUIVO_PRESENCAS):
        pd.DataFrame(columns=["Data", "Cliente", "Serviço Usado", "Barbeiro Atendeu"]).to_csv(ARQUIVO_PRESENCAS, index=False, encoding='utf-8')

inicializar_banco_de_dados()

servicos_df = pd.read_csv(ARQUIVO_SERVICOS, encoding='utf-8')
produtos_df = pd.read_csv(ARQUIVO_PRODUTOS, encoding='utf-8')
vendas_df = pd.read_csv(ARQUIVO_VENDAS, encoding='utf-8')
gastos_df = pd.read_csv(ARQUIVO_GASTOS, encoding='utf-8')
barbeiros_df = pd.read_csv(ARQUIVO_BARBEIROS, encoding='utf-8')
assinaturas_df = pd.read_csv(ARQUIVO_ASSINATURAS, encoding='utf-8')
presencas_df = pd.read_csv(ARQUIVO_PRESENCAS, encoding='utf-8')

# --- SESSÃO DE LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "perfil" not in st.session_state:
    st.session_state["perfil"] = None
if "carrinho_comanda" not in st.session_state:
    st.session_state["carrinho_comanda"] = []

if not st.session_state["autenticado"]:
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>💈 Painel de Controle Oficial</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6B7280;'>Introduza as suas credenciais para gerir a barbearia</p>", unsafe_allow_html=True)
    
    col_login, _ = st.columns([1, 2])
    with col_login:
        with st.container(border=True):
            usuario = st.text_input("Usuário:")
            senha = st.text_input("Senha:", type="password")
            if st.button("🔓 Entrar no Sistema", type="primary", use_container_width=True):
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

# --- DESIGN DO MENU LATERAL ---
st.sidebar.markdown("<h2 style='color: #1E3A8A; text-align: center;'>✂️ CredForte Menu</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"Perfil Ativo: **{st.session_state['perfil'].upper()}**")
st.sidebar.markdown("---")

if st.session_state["perfil"] == "admin":
    opcoes_menu = ["💸 Abrir Comanda (Vendas)", "💳 Clube de Assinaturas", "📉 Lançar Gasto/Despesa", "👥 Cadastrar Barbeiro", "📦 Estoque & Serviços", "⚙️ Gerenciar Catálogo", "📊 Painel de Relatórios", "⚙️ Configurações"]
else:
    opcoes_menu = ["💸 Abrir Comanda (Vendas)", "📦 Estoque & Serviços"]

menu = st.sidebar.radio("Escolha uma Aba:", opcoes_menu)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair com Segurança", use_container_width=True):
    st.session_state["autenticado"] = False
    st.session_state["perfil"] = None
    st.session_state["carrinho_comanda"] = []
    st.rerun()

# ---------------- MÓDULO 1: COMANDA ELETRÔNICA (VISUAL MELHORADO) ----------------
if menu == "💸 Abrir Comanda (Vendas)":
    st.markdown("<h2 style='color: #1E3A8A;'>📋 Caixa Geral e Comanda Eletrônica</h2>", unsafe_allow_html=True)
    st.markdown("Adicione os consumos do cliente passo a passo antes de fechar a conta única.")
    
    col_com1, col_com2 = st.columns([1, 1], gap="large")
    
    with col_com1:
        with st.container(border=True):
            st.markdown("#### ➕ Adicionar Item")
            tipo = st.selectbox("Selecione a Categoria:", ["Serviço (Corte/Barba)", "Produto (Bebida/Pomada)"])
            
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
                
            item_selecionado = st.selectbox("Selecione o Item do Catálogo:", lista_itens)
            qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1)
            
            preco_unitario = tabela_ref[tabela_ref.iloc[:, 1] == item_selecionado][nome_col_preco].values[0]
            subtotal_item = float(preco_unitario) * qtd
            
            st.markdown(f"**Subtotal do item:** R$ {subtotal_item:.2f}")
            if st.button("➕ Inserir no Carrinho", use_container_width=True):
                st.session_state["carrinho_comanda"].append({
                    "Item": item_selecionado, "Tipo": categoria_venda, "Quantidade": qtd, "Valor Total": subtotal_item
                })
                st.toast(f"'{item_selecionado}' adicionado!")
                st.rerun()

    with col_com2:
        with st.container(border=True):
            st.markdown("#### 🛒 Itens Consumidos")
            if len(st.session_state["carrinho_comanda"]) > 0:
                df_temp_carrinho = pd.DataFrame(st.session_state["carrinho_comanda"])
                st.dataframe(df_temp_carrinho, use_container_width=True, hide_index=True)
                
                valor_total_comanda = df_temp_carrinho["Valor Total"].sum()
                st.markdown(f"<h3 style='color: #1E3A8A;'>Total da Conta: R$ {valor_total_comanda:.2f}</h3>", unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("#### 🏁 Fechamento e Recebimento")
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    forma_pagamento = st.selectbox("Forma de Recebimento:", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
                    lista_barbeiros_sistema = barbeiros_df["Nome"].tolist() if not barbeiros_df.empty else ["G."]
                    barbeiro_venda = st.selectbox("Barbeiro Executor:", lista_barbeiros_sistema)
                with c_f2:
                    cliente = st.text_input("Identificação do Cliente:", value="Avulso")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 Finalizar Conta e Lançar no Caixa", type="primary", use_container_width=True):
                    data_atual = datetime.now().strftime("%Y-%m-%d")
                    novas_linhas = []
                    for item_c in st.session_state["carrinho_comanda"]:
                        item_c["Data"] = data_atual
                        item_c["Forma de Pagamento"] = forma_pagamento
                        item_c["Barbeiro"] = barbeiro_venda
                        item_c["Cliente"] = cliente
                        novas_linhas.append(item_c)
                    
                    vendas_df = pd.concat([vendas_df, pd.DataFrame(novas_linhas)], ignore_index=True)
                    vendas_df.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
                    st.session_state["carrinho_comanda"] = []
                    st.success(f"✅ Venda de R$ {valor_total_comanda:.2f} processada com sucesso!")
                    time.sleep(1.2)
                    st.rerun()
                    
                if st.button("🗑️ Esvaziar Comanda", use_container_width=True):
                    st.session_state["carrinho_comanda"] = []
                    st.rerun()
            else:
                st.info("A comanda eletrônica está limpa e vazia neste momento.")

# ---------------- MÓDULO 2: CLUBE DE ASSINATURAS (VISUAL DE ALERTAS PREMIUM) ----------------
elif menu == "💳 Clube de Assinaturas" and st.session_state["perfil"] == "admin":
    st.markdown("<h2 style='color: #1E3A8A;'>💳 Controle do Clube de Assinaturas</h2>", unsafe_allow_html=True)
    
    tab_ass1, tab_ass2, tab_ass3 = st.tabs(["👥 Lista e Controle de Membros", "🪪 Check-in de Presença", "📊 Relatório de Frequência"])
    
    with tab_ass1:
        with st.container(border=True):
            st.markdown("#### ✍️ Matricular Novo Cliente no Clube")
            col_as1, col_as2, col_as3 = st.columns(3)
            with col_as1:
                nome_ass = st.text_input("Nome Completo do Assinante:")
                plano_ass = st.selectbox("Plano Contratado:", ["Plano Mensal - Corte + Barba", "Plano Individual - Apenas Corte"])
            with col_as2:
                valor_ass = st.number_input("Taxa de Adesão Mensal (R$):", min_value=0.0, value=110.0)
                data_pago = st.date_input("Data do Recebimento/Início:", datetime.now())
            with col_as3:
                forma_pago_ass = st.selectbox("Canal de Recebimento:", ["Pix", "Dinheiro", "Cartão"])
            
            if st.button("🔥 Ativar Plano do Cliente", type="primary", use_container_width=True):
                if nome_ass != "":
                    venc_calc = (data_pago + timedelta(days=30)).strftime("%Y-%m-%d")
                    nova_ass = pd.DataFrame([{
                        "Cliente": nome_ass, "Plano": plano_ass, "Data Inicio": data_pago.strftime("%Y-%m-%d"),
                        "Data Vencimento": venc_calc, "Valor Mensal": valor_ass
                    }])
                    assinaturas_df = pd.concat([assinaturas_df, nova_ass], ignore_index=True)
                    assinaturas_df.to_csv(ARQUIVO_ASSINATURAS, index=False, encoding='utf-8')
                    
                    venda_ass = pd.DataFrame([{
                        "Data": data_pago.strftime("%Y-%m-%d"), "Item": f"Clube: {plano_ass}",
                        "Tipo": "Serviço", "Quantidade": 1, "Valor Total": valor_ass,
                        "Forma de Pagamento": forma_pago_ass, "Barbeiro": "ADMIN", "Cliente": nome_ass
                    }])
                    vendas_df = pd.concat([vendas_df, venda_ass], ignore_index=True)
                    vendas_df.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
                    
                    st.success(f"✅ Assinatura ativa! Vencimento definido para {venc_calc}")
                    time.sleep(1.2)
                    st.rerun()
                    
        st.markdown("<br>#### 🔔 Monitoramento Técnico de Vencimentos (Planos 30 dias)", unsafe_allow_html=True)
        if not assinaturas_df.empty:
            data_hoje = datetime.now().date()
            for idx, r in assinaturas_df.iterrows():
                venc_date = datetime.strptime(r["Data Vencimento"], "%Y-%m-%d").date()
                dias_restantes = (venc_date - data_hoje).days
                
                # Alertas visuais muito mais chamativos
                if dias_restantes < 0:
                    st.error(f"🔴 **{r['Cliente']}** | Plano: {r['Plano']} | Venceu em: {r['Data Vencimento']} (**Vencido há {abs(dias_restantes)} dias - Bloquear e Cobrar!**)")
                elif dias_restantes <= 5:
                    st.warning(f"⚠️ **{r['Cliente']}** | Plano: {r['Plano']} | Vencimento: {r['Data Vencimento']} (**Atenção: Restam apenas {dias_restantes} dias para expirar!**)")
                else:
                    st.info(f"🟢 **{r['Cliente']}** | Plano: {r['Plano']} | Vencimento: {r['Data Vencimento']} (Regular: {dias_restantes} dias restantes)")
        else:
            st.info("Nenhum assinante cadastrado.")

    with tab_ass2:
        with st.container(border=True):
            st.markdown("#### 🪪 Registrar Entrada de Assinante (Sem Cobrança)")
            if not assinaturas_df.empty:
                cliente_uso = st.selectbox("Selecione o Cliente do Clube:", assinaturas_df["Cliente"].tolist())
                servico_uso = st.selectbox("Qual o procedimento do dia?", ["Corte de Cabelo", "Fazer a Barba", "Corte + Barba"])
                lista_barbeiros_sistema = barbeiros_df["Nome"].tolist() if not barbeiros_df.empty else ["G."]
                barbeiro_atendeu = st.selectbox("Barbeiro Responsável:", lista_barbeiros_sistema)
                
                if st.button("💾 Validar Presença e Uso", type="primary", use_container_width=True):
                    nova_presenca = pd.DataFrame([{
                        "Data": datetime.now().strftime("%Y-%m-%d"), "Cliente": cliente_uso,
                        "Serviço Usado": servico_uso, "Barbeiro Atendeu": barbeiro_atendeu
                    }])
                    presencas_df = pd.concat([presencas_df, nova_presenca], ignore_index=True)
                    presencas_df.to_csv(ARQUIVO_PRESENCAS, index=False, encoding='utf-8')
                    st.success(f"✅ Check-in realizado! Presença salva para {cliente_uso}.")
                    time.sleep(1.2)
                    st.rerun()
            else:
                st.info("Nenhum assinante cadastrado.")

    with tab_ass3:
        st.markdown("#### 📈 Frequência Mensal de Membros do Clube")
        if not presencas_df.empty:
            contagem_visitas = presencas_df.groupby("Cliente")["Serviço Usado"].count().reset_index()
            contagem_visitas.columns = ["Nome do Cliente Assinante", "Quantidade de vezes que usou no mês"]
            st.dataframe(contagem_visitas, use_container_width=True, hide_index=True)
            st.markdown("---")
            st.dataframe(presencas_df.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("Nenhuma presença registrada ainda.")

# ---------------- MÓDULO 3: LANÇAR GASTO ----------------
elif menu == "📉 Lançar Gasto/Despesa" and st.session_state["perfil"] == "admin":
    st.markdown("<h2 style='color: #1E3A8A;'>📉 Lançamento de Gastos e Custos operacionais</h2>", unsafe_allow_html=True)
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            descricao = st.text_input("Descrição da Saída:")
            valor_gasto = st.number_input("Valor Pago em Dinheiro (R$):", min_value=0.0, step=0.50)
        with col2:
            categoria = st.selectbox("Categoria do Custo:", ["Infraestrutura (Luz/Água/Aluguel)", "Produtos (Reposição de Estoque)", "Equipamentos/Ferramentas", "Outros"])
            
        if st.button("💾 Gravar Custo no Fluxo", type="primary", use_container_width=True):
            if descricao != "" and valor_gasto > 0:
                novo_gasto = pd.DataFrame([{
                    "Data": datetime.now().strftime("%Y-%m-%d"), "Descrição": descricao, "Valor (R$)": valor_gasto, "Categoria": categoria
                }])
                gastos_df = pd.concat([gastos_df, novo_gasto], ignore_index=True)
                gastos_df.to_csv(ARQUIVO_GASTOS, index=False, encoding='utf-8')
                st.success(f"✅ Despesa '{descricao}' registrada com sucesso!")
                time.sleep(1.2)
                st.rerun()

# ---------------- MÓDULO 4: GERENCIAR BARBEIROS ----------------
elif menu == "👥 Cadastrar Barbeiro" and st.session_state["perfil"] == "admin":
    st.markdown("<h2 style='color: #1E3A8A;'>👥 Gestão da Equipe de Profissionais</h2>", unsafe_allow_html=True)
    col_cad1, col_cad2 = st.columns(2, gap="large")
    with col_cad1:
        with st.container(border=True):
            st.markdown("#### ➕ Adicionar Barbeiro")
            novo_nome = st.text_input("Nome Comercial:")
            nova_comissao = st.number_input("Comissão nos Serviços (%):", min_value=0.0, max_value=100.0, value=50.0, step=5.0)
            
            if st.button("Cadastrar Novo Barbeiro", type="primary", use_container_width=True):
                if novo_nome != "" and novo_nome not in barbeiros_df["Nome"].tolist():
                    novo_b = pd.DataFrame([{"Nome": novo_nome, "Comissão (%)": nova_comissao}])
                    barbeiros_df = pd.concat([barbeiros_df, novo_b], ignore_index=True)
                    barbeiros_df.to_csv(ARQUIVO_BARBEIROS, index=False, encoding='utf-8')
                    st.success(f"👤 Profissional '{novo_nome}' ativo no sistema!")
                    time.sleep(1.2)
                    st.rerun()
                    
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("#### ❌ Desativar/Remover Barbeiro")
            if not barbeiros_df.empty:
                barbeiro_remover = st.selectbox("Selecione o Nome para Exclusão:", barbeiros_df["Nome"].tolist())
                if st.button("Remover Permanentemente", use_container_width=True):
                    barbeiros_df = barbeiros_df[barbeiros_df["Nome"] != barbeiro_remover]
                    barbeiros_df.to_csv(ARQUIVO_BARBEIROS, index=False, encoding='utf-8')
                    st.success(f"🗑️ Profissional '{barbeiro_remover}' removido.")
                    time.sleep(1.2)
                    st.rerun()
            else:
                st.info("Sem profissionais ativos.")
    with col_cad2:
        st.markdown("#### Lista de Profissionais Contratados")
        st.dataframe(barbeiros_df, use_container_width=True, hide_index=True)

# ---------------- MÓDULO 5: ESTOQUE & SERVIÇOS ----------------
elif menu == "📦 Estoque & Serviços":
    st.markdown("<h2 style='color: #1E3A8A;'>📦 Monitor de Estoque e Serviços</h2>", unsafe_allow_html=True)
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    produtos_calculados = produtos_df.copy()
    qtd_vendida_map = vendas_df[vendas_df["Tipo"] == "Produto"].groupby("Item")["Quantidade"].sum().to_dict()
    
    produtos_calculados["Quantidade Vendida"] = produtos_calculados["Nome do Produto"].map(qtd_vendida_map).fillna(0).astype(int)
    produtos_calculados["Estoque Atual"] = produtos_calculados["Estoque Inicial"] - produtos_calculados["Quantidade Vendida"]
    
    with st.container(border=True):
        st.markdown("#### 📦 Nível de Prateleira (Produtos)")
        st.dataframe(produtos_calculados, use_container_width=True, hide_index=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("#### 💈 Tabela Vigente de Serviços")
        st.dataframe(servicos_df, use_container_width=True, hide_index=True)

# ---------------- MÓDULO 6: GERENCIAR CATÁLOGO ----------------
elif menu == "⚙️ Gerenciar Catálogo" and st.session_state["perfil"] == "admin":
    st.markdown("<h2 style='color: #1E3A8A;'>⚙️ Alteração de Tabela e Preços</h2>", unsafe_allow_html=True)
    aba_serv, aba_prod = st.tabs(["💈 Menu de Serviços", "📦 Menu de Produtos"])
    
    with aba_serv:
        with st.container(border=True):
            st.markdown("#### Adicionar Novo Serviço")
            s_nome = st.text_input("Nome do Serviço:")
            s_preco = st.number_input("Valor Cobrado (R$):", min_value=0.0, value=20.0, step=5.0)
            if st.button("Criar Serviço", type="primary"):
                if s_nome != "":
                    novo_id = int(servicos_df["ID"].max() + 1) if not servicos_df.empty else 1
                    novo_s = pd.DataFrame([{"ID": novo_id, "Nome do Serviço": s_nome, "Preço (R$)": s_preco}])
                    servicos_df = pd.concat([servicos_df, novo_s], ignore_index=True)
                    servicos_df.to_csv(ARQUIVO_SERVICOS, index=False, encoding='utf-8')
                    st.success("✨ Serviço criado!")
                    time.sleep(1.2)
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("#### Mudar Preço Existente")
            servico_editar = st.selectbox("Escolha o Serviço:", servicos_df["Nome do Serviço"].tolist())
            novo_preco_s = st.number_input("Modificar Valor para (R$):", min_value=0.0, value=float(servicos_df[servicos_df["Nome do Serviço"] == servico_editar]["Preço (R$)"].values[0]))
            if st.button("Atualizar Valor"):
                servicos_df.loc[servicos_df["Nome do Serviço"] == servico_editar, "Preço (R$)"] = novo_preco_s
                servicos_df.to_csv(ARQUIVO_SERVICOS, index=False, encoding='utf-8')
                st.success("🎉 Tabela atualizada!")
                time.sleep(1.2)
                st.rerun()

    with aba_prod:
        with st.container(border=True):
            st.markdown("#### Cadastrar Novo Produto")
            col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
            with col_p1: p_nome = st.text_input("Nome Comercial do Produto:")
            with col_p2: p_venda = st.number_input("Preço de Venda:", min_value=0.0, value=10.0)
            with col_p3: p_custo = st.number_input("Preço de Custo:", min_value=0.0, value=5.0)
            with col_p4: p_estoque = st.number_input("Estoque Adquirido:", min_value=0, value=10)
            with col_p5: p_comis = st.number_input("Comissão do Barbeiro:", min_value=0.0, value=0.0)
                
            if st.button("Salvar Produto nas Prateleiras", type="primary", use_container_width=True):
                if p_nome != "":
                    novo_id = int(produtos_df["ID"].max() + 1) if not produtos_df.empty else 1
                    novo_p = pd.DataFrame([{"ID": novo_id, "Nome do Produto": p_nome, "Preço de Venda": p_venda, "Preço de Custo": p_custo, "Estoque Inicial": p_estoque, "Comissão Barbeiro (R$)": p_comis}])
                    produtos_df = pd.concat([produtos_df, novo_p], ignore_index=True)
                    produtos_df.to_csv(ARQUIVO_PRODUTOS, index=False, encoding='utf-8')
                    st.success("📦 Produto inserido!")
                    time.sleep(1.2)
                    st.rerun()
                    
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("#### Editar Produto Existente / Reposição de Estoque")
            prod_editar = st.selectbox("Selecione o Produto:", produtos_df["Nome do Produto"].tolist())
            col_ed1, col_ed2, col_ed3, col_ed4 = st.columns(4)
            item_linha = produtos_df[produtos_df["Nome do Produto"] == prod_editar]
            with col_ed1: ed_venda = st.number_input("Ajustar Preço Venda:", value=float(item_linha["Preço de Venda"].values[0]))
            with col_ed2: ed_custo = st.number_input("Ajustar Preço Custo:", value=float(item_linha["Preço de Custo"].values[0]))
            with col_ed3: ed_estoque = st.number_input("Ajustar Estoque Inicial:", value=int(item_linha["Estoque Inicial"].values[0]))
            with col_ed4: ed_comis = st.number_input("Ajustar Comissão Fixa (R$):", value=float(item_linha["Comissão Barbeiro (R$)"].values[0]))
                
            if st.button("Salvar Modificações Finais", use_container_width=True):
                produtos_df.loc[produtos_df["Nome do Produto"] == prod_editar, ["Preço de Venda", "Preço de Custo", "Estoque Inicial", "Comissão Barbeiro (R$)"]] = [ed_venda, ed_custo, ed_estoque, ed_comis]
                produtos_df.to_csv(ARQUIVO_PRODUTOS, index=False, encoding='utf-8')
                st.success("🔥 Informações atualizadas!")
                time.sleep(1.2)
                st.rerun()

# ---------------- MÓDULO 7: PAINEL DE RELATÓRIOS (DESIGN PREMIUM EM CARTÕES) ----------------
elif menu == "📊 Painel de Relatórios" and st.session_state["perfil"] == "admin":
    st.markdown("<h2 style='color: #1E3A8A;'>📊 Dashboard e Fechamento Financeiro</h2>", unsafe_allow_html=True)
    
    vendas_df["Valor Total"] = pd.to_numeric(vendas_df["Valor Total"], errors='coerce').fillna(0)
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    gastos_df["Valor (R$)"] = pd.to_numeric(gastos_df["Valor (R$)"], errors='coerce').fillna(0)
    
    faturamento = vendas_df["Valor Total"].sum()
    total_gastos = gastos_df["Valor (R$)"].sum()
    lucro_liquido = faturamento - total_gastos
    
    # EFEITO DE CARTÕES USANDO CONTAINER EM COLUNAS
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown("<p style='color: #6B7280; font-size: 14px; margin:0;'>💰 FATURAMENTO BRUTO</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: #10B981; margin:0;'>R$ {faturamento:.2f}</h2>", unsafe_allow_html=True)
    with c2:
        with st.container(border=True):
            st.markdown("<p style='color: #6B7280; font-size: 14px; margin:0;'>📉 TOTAL DE GASTOS</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: #EF4444; margin:0;'>R$ {total_gastos:.2f}</h2>", unsafe_allow_html=True)
    with c3:
        with st.container(border=True):
            st.markdown("<p style='color: #6B7280; font-size: 14px; margin:0;'>🔥 LUCRO LÍQUIDO REAL</p>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: #1E3A8A; margin:0;'>R$ {lucro_liquido:.2f}</h2>", unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("#### 💸 Tabela Unificada de Comissões Semanal")
        if not barbeiros_df.empty:
            relatorio_comissao = []
            mapa_comissao_produto = produtos_df.set_index("Nome do Produto")["Comissão Barbeiro (R$)"].to_dict()
            
            for _, b in barbeiros_df.iterrows():
                nome_b = b["Nome"]
                porcentagem_servico = b["Comissão (%)"]
                vendas_do_barbeiro = vendas_df[vendas_df["Barbeiro"] == nome_b]
                
                # Serviços
                servicos_b = vendas_do_barbeiro[vendas_do_barbeiro["Tipo"] == "Serviço"]
                faturamento_servicos = servicos_b["Valor Total"].sum()
                total_cortes = servicos_b["Quantidade"].sum()
                valor_comissao_servico = faturamento_servicos * (porcentagem_servico / 100.0)
                
                # Produtos
                produtos_b = vendas_do_barbeiro[vendas_do_barbeiro["Tipo"] == "Produto"]
                valor_comissao_produto = 0.0
                total_produtos_vendidos = produtos_b["Quantidade"].sum()
                
                for _, venda_p in produtos_b.iterrows():
                    nome_p = venda_p["Item"]
                    qtd_p = venda_p["Quantidade"]
                    comissao_unitaria_p = mapa_comissao_produto.get(nome_p, 0.0)
                    valor_comissao_produto += float(comissao_unitaria_p) * float(qtd_p)
                    
                total_geral_a_pagar = valor_comissao_servico + valor_comissao_produto
                
                relatorio_comissao.append({
                    "Barbeiro": nome_b, "Qtd Serviços": int(total_cortes),
                    "Comissão Serviços": f"R$ {valor_comissao_servico:.2f} ({int(porcentagem_servico)}%)",
                    "Qtd Produtos": int(total_produtos_vendidos), "Comissão Produtos": f"R$ {valor_comissao_produto:.2f}",
                    "TOTAL A PAGAR DE COMISSÃO": f"R$ {total_geral_a_pagar:.2f}"
                })
            st.dataframe(pd.DataFrame(relatorio_comissao), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum barbeiro ativo cadastrado.")
            
    st.markdown("<br>", unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2, gap="large")
    with col_g1:
        st.markdown("#### 📅 Desempenho Faturamento Diário")
        if not vendas_df.empty: 
            st.line_chart(vendas_df.groupby("Data")["Valor Total"].sum())
    with col_g2:
        st.markdown("#### 💰 Balanço Balcão (Serviços vs Produtos)")
        if not vendas_df.empty: 
            st.bar_chart(vendas_df.groupby("Tipo")["Valor Total"].sum())

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Histórico Completo de Vendas", "📉 Histórico Geral de Gastos"])
    with tab1: st.dataframe(vendas_df.sort_index(ascending=False), use_container_width=True, hide_index=True)
    with tab2: st.dataframe(gastos_df.sort_index(ascending=False), use_container_width=True, hide_index=True)

# ---------------- MÓDULO 8: CONFIGURAÇÕES ----------------
elif menu == "⚙️ Configurações" and st.session_state["perfil"] == "admin":
    st.markdown("<h2 style='color: #1E3A8A;'>⚙️ Configurações Críticas</h2>", unsafe_allow_html=True)
    with st.container(border=True):
        st.warning("Ação destrutiva. Ao clicar no botão abaixo limpa todas as vendas do banco de dados definitivamente.")
        if st.button("🚨 Limpar Todas as Vendas e Zerar Caixa", type="primary", use_container_width=True):
            pd.DataFrame(columns=["Data", "Item", "Tipo", "Quantidade", "Valor Total", "Forma de Pagamento", "Barbeiro", "Cliente"]).to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
            st.success("Sistema redefinido com faturamento zerado!")
            st.rerun()
