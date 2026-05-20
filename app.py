import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time

# Configuração da página da Barbearia com o nome oficial completo
st.set_page_config(page_title="O Chefão Barbearia e Conveniência", layout="wide", initial_sidebar_state="expanded")

# Bancos de dados em formato CSV
ARQUIVO_SERVICOS = "servicos.csv"
ARQUIVO_PRODUTOS = "produtos.csv"
ARQUIVO_VENDAS = "vendas.csv"
ARQUIVO_GASTOS = "gastos.csv"
ARQUIVO_BARBEIROS = "barbeiros.csv"
ARQUIVO_ASSINATURAS = "assinaturas.csv"
ARQUIVO_PRESENCAS = "presencas.csv"
ARQUIVO_USUARIOS = "usuarios.csv"
ARQUIVO_SESSAO = "sessao_ativa.csv"

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
        
    if not os.path.exists(ARQUIVO_USUARIOS):
        pd.DataFrame([{"Usuario": "admin", "Senha": "barba123", "Permissoes": "TODAS"}]).to_csv(ARQUIVO_USUARIOS, index=False, encoding='utf-8')

    if not os.path.exists(ARQUIVO_SESSAO):
        pd.DataFrame(columns=["Usuario", "ValidoAte"]).to_csv(ARQUIVO_SESSAO, index=False, encoding='utf-8')

inicializar_banco_de_dados()

# Carregar dados dos usuários do arquivo
usuarios_df = pd.read_csv(ARQUIVO_USUARIOS, encoding='utf-8')

# --- LISTA MESTRE DE PERMISSÕES ---
PERMISSOES_MASTER = ["💸 Abrir Comanda (Vendas)", "💳 Clube de Assinaturas", "📉 Lançar Gasto/Despesa", "✏️ Corrigir Lançamentos", "👥 Cadastrar Barbeiro", "📦 Estoque & Serviços", "⚙️ Gerenciar Catálogo", "👤 Gerenciar Usuários", "📊 Painel de Relatórios", "⚙️ Configurações"]
PERMISSOES_PADRAO = ["💸 Abrir Comanda (Vendas)", "📦 Estoque & Serviços"]

# --- CONTROLE DE SESSÃO EM DISCO ---
def verificar_sessao_salva():
    if os.path.exists(ARQUIVO_SESSAO):
        try:
            df_s = pd.read_csv(ARQUIVO_SESSAO, encoding='utf-8')
            if not df_s.empty:
                usuario_salvo = str(df_s.iloc[0]["Usuario"]).strip().lower()
                valido_ate_str = df_s.iloc[0]["ValidoAte"]
                valido_ate = datetime.strptime(valido_ate_str, "%Y-%m-%d %H:%M:%S")
                if datetime.now() < valido_ate:
                    return usuario_salvo
        except:
            pass
    return None

def salvar_sessao_em_disco(usuario):
    tempo_limite = datetime.now() + timedelta(hours=2)
    df_s = pd.DataFrame([{"Usuario": str(usuario).strip().lower(), "ValidoAte": tempo_limite.strftime("%Y-%m-%d %H:%M:%S")}])
    df_s.to_csv(ARQUIVO_SESSAO, index=False, encoding='utf-8')

def destruir_sessao_em_disco():
    if os.path.exists(ARQUIVO_SESSAO):
        pd.DataFrame(columns=["Usuario", "ValidoAte"]).to_csv(ARQUIVO_SESSAO, index=False, encoding='utf-8')

# --- LOGICA DE VERIFICAÇÃO AUTOMÁTICA AO ENTRAR ---
usuario_detectado = verificar_sessao_salva()

if usuario_detectado:
    st.session_state["autenticado"] = True
    st.session_state["perfil"] = usuario_detectado
    
    # Buscar permissões forçando letras minúsculas para não dar erro de digitação
    usuarios_df["Usuario_Lower"] = usuarios_df["Usuario"].str.strip().str.lower()
    u_linha = usuarios_df[usuarios_df["Usuario_Lower"] == usuario_detectado]
    
    if not u_linha.empty:
        perm_string = u_linha.iloc[0]["Permissoes"]
        if perm_string == "TODAS":
            st.session_state["permissoes_usuario"] = PERMISSOES_MASTER
        else:
            st.session_state["permissoes_usuario"] = perm_string.split("|")
    else:
        st.session_state["permissoes_usuario"] = PERMISSOES_PADRAO
else:
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False
    if "perfil" not in st.session_state:
        st.session_state["perfil"] = None
    if "permissoes_usuario" not in st.session_state:
        st.session_state["permissoes_usuario"] = PERMISSOES_PADRAO

if "carrinho_comanda" not in st.session_state:
    st.session_state["carrinho_comanda"] = []

# --- TELA DE LOGIN ---
if not st.session_state["autenticado"]:
    st.title("💈 O Chefão Barbearia e Conveniência")
    st.write("Entre com suas credenciais para gerenciar o sistema")
    
    col_login, _ = st.columns([1, 2])
    with col_login:
        with st.container(border=True):
            input_usuario = st.text_input("Usuário:").strip().lower()
            input_senha = st.text_input("Senha:", type="password")
            if st.button("🔓 Acessar Sistema", type="primary", use_container_width=True):
                usuarios_df["Usuario_Lower"] = usuarios_df["Usuario"].str.strip().str.lower()
                usuario_valido = usuarios_df[(usuarios_df["Usuario_Lower"] == input_usuario) & (usuarios_df["Senha"] == input_senha)]
                
                if not usuario_valido.empty:
                    st.session_state["autenticado"] = True
                    st.session_state["perfil"] = input_usuario
                    salvar_sessao_em_disco(input_usuario)
                    
                    perm_string = usuario_valido.iloc[0]["Permissoes"]
                    if perm_string == "TODAS":
                        st.session_state["permissoes_usuario"] = PERMISSOES_MASTER
                    else:
                        st.session_state["permissoes_usuario"] = perm_string.split("|")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos!")
    st.stop()

# Estender o temporizador de sessão a cada clique
salvar_sessao_em_disco(st.session_state["perfil"])

# Carregar o resto do banco de dados
servicos_df = pd.read_csv(ARQUIVO_SERVICOS, encoding='utf-8')
produtos_df = pd.read_csv(ARQUIVO_PRODUTOS, encoding='utf-8')
vendas_df = pd.read_csv(ARQUIVO_VENDAS, encoding='utf-8')
gastos_df = pd.read_csv(ARQUIVO_GASTOS, encoding='utf-8')
barbeiros_df = pd.read_csv(ARQUIVO_BARBEIROS, encoding='utf-8')
assinaturas_df = pd.read_csv(ARQUIVO_ASSINATURAS, encoding='utf-8')
presencas_df = pd.read_csv(ARQUIVO_PRESENCAS, encoding='utf-8')

# --- CONFIGURAÇÃO DA BARRA LATERAL ---
st.sidebar.title("✂️ O Chefão")
st.sidebar.write(f"Conectado como: **{st.session_state['perfil'].upper()}**")
st.sidebar.markdown("---")

# Garante que a lista de menus nunca esteja vazia para evitar travar o st.sidebar.radio
menus_validos = st.session_state["permissoes_usuario"] if st.session_state["permissoes_usuario"] else PERMISSOES_PADRAO
menu = st.sidebar.radio("Navegação:", menus_validos)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair com Segurança", use_container_width=True):
    st.session_state["autenticado"] = False
    st.session_state["perfil"] = None
    st.session_state["permissoes_usuario"] = []
    st.session_state["carrinho_comanda"] = []
    destruir_sessao_em_disco()
    st.rerun()

# ---------------- MÓDULO 1: COMANDA ELETRÔNICA ----------------
if menu == "💸 Abrir Comanda (Vendas)":
    st.header("📋 Caixa e Comanda Eletrônica - O Chefão")
    st.write("Adicione os consumos de barbearia e conveniência do cliente.")
    col_com1, col_com2 = st.columns([1, 1], gap="large")
    with col_com1:
        with st.container(border=True):
            st.subheader("➕ Adicionar Item")
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
            st.write(f"**Subtotal do item:** R$ {subtotal_item:.2f}")
            if st.button("➕ Inserir na Comanda", use_container_width=True):
                st.session_state["carrinho_comanda"].append({
                    "Item": item_selecionado, "Tipo": categoria_venda, "Quantidade": qtd, "Valor Total": subtotal_item
                })
                st.toast(f"'{item_selecionado}' adicionado!")
                st.rerun()
    with col_com2:
        with st.container(border=True):
            st.subheader("🛒 Resumo Consumo")
            if len(st.session_state["carrinho_comanda"]) > 0:
                df_temp_carrinho = pd.DataFrame(st.session_state["carrinho_comanda"])
                st.dataframe(df_temp_carrinho, use_container_width=True, hide_index=True)
                valor_total_comanda = df_temp_carrinho["Valor Total"].sum()
                st.markdown(f"### Total Geral: R$ {valor_total_comanda:.2f}")
                st.markdown("---")
                st.subheader("🏁 Recebimento")
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    forma_pagamento = st.selectbox("Forma de Recebimento:", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
                    lista_barbeiros_sistema = barbeiros_df["Nome"].tolist() if not barbeiros_df.empty else ["G."]
                    barbeiro_venda = st.selectbox("Barbeiro Executor:", lista_barbeiros_sistema)
                with c_f2:
                    cliente = st.text_input("Identificação do Cliente:", value="Avulso")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 Finalizar Conta e Registrar", type="primary", use_container_width=True):
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
                    st.success(f"✅ Venda de R$ {valor_total_comanda:.2f} processada!")
                    time.sleep(1.2)
                    st.rerun()
                if st.button("🗑️ Esvaziar Comanda", use_container_width=True):
                    st.session_state["carrinho_comanda"] = []
                    st.rerun()
            else:
                st.info("A comanda eletrônica está limpa e vazia.")

# ---------------- MÓDULO 2: CLUBE DE ASSINATURAS ----------------
elif menu == "💳 Clube de Assinaturas":
    st.header("💳 Clube de Assinaturas")
    tab_ass1, tab_ass2, tab_ass3 = st.tabs(["👥 Membros Ativos", "🪪 Check-in de Presença", "📊 Frequência do Plano"])
    with tab_ass1:
        with st.container(border=True):
            st.subheader("### ✍️ Matricular Cliente no Clube")
            col_as1, col_as2, col_as3 = st.columns(3)
            with col_as1:
                nome_ass = st.text_input("Nome do Assinante:")
                plano_ass = st.selectbox("Plano Contratado:", ["Plano Mensal - Corte + Barba", "Plano Individual - Apenas Corte"])
            with col_as2:
                valor_ass = st.number_input("Taxa de Adesão Mensal (R$):", min_value=0.0, value=110.0)
                data_pago = st.date_input("Data de Início:", datetime.now())
            with col_as3:
                forma_pago_ass = st.selectbox("Canal de Recebimento:", ["Pix", "Dinheiro", "Cartão"])
            if st.button("🔥 Ativar Plano", type="primary", use_container_width=True):
                if nome_ass != "":
                    venc_calc = (data_pago + timedelta(days=30)).strftime("%Y-%m-%d")
                    nova_ass = pd.DataFrame([{"Cliente": nome_ass, "Plano": plano_ass, "Data Inicio": data_pago.strftime("%Y-%m-%d"), "Data Vencimento": venc_calc, "Valor Mensal": valor_ass}])
                    assinaturas_df = pd.concat([assinaturas_df, nova_ass], ignore_index=True)
                    assinaturas_df.to_csv(ARQUIVO_ASSINATURAS, index=False, encoding='utf-8')
                    venda_ass = pd.DataFrame([{"Data": data_pago.strftime("%Y-%m-%d"), "Item": f"Clube: {plano_ass}", "Tipo": "Serviço", "Quantidade": 1, "Valor Total": valor_ass, "Forma de Pagamento": forma_pago_ass, "Barbeiro": "ADMIN", "Cliente": nome_ass}])
                    vendas_df = pd.concat([vendas_df, venda_ass], ignore_index=True)
                    vendas_df.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
                    st.success(f"✅ Assinatura activa! Vencimento definido para {venc_calc}")
                    time.sleep(1.2)
                    st.rerun()
        st.markdown("<br>### 🔔 Status de Planos (Ciclo de 30 dias)", unsafe_allow_html=True)
        if not assinaturas_df.empty:
            data_hoje = datetime.now().date()
            for idx, r in assinaturas_df.iterrows():
                venc_date = datetime.strptime(r["Data Vencimento"], "%Y-%m-%d").date()
                dias_restantes = (venc_date - data_hoje).days
                if dias_restantes < 0:
                    st.error(f"🔴 **{r['Cliente']}** | Venceu em: {r['Data Vencimento']} (Bloqueado - Realizar Cobrança!)")
                elif dias_restantes <= 5:
                    st.warning(f"⚠️ **{r['Cliente']}** | Vence em: {r['Data Vencimento']} (Atenção: Restam {dias_restantes} dias para expirar!)")
                else:
                    st.info(f"🟢 **{r['Cliente']}** | Vencimento: {r['Data Vencimento']} (Regular: {dias_restantes} dias)")
            st.markdown("---")
            st.subheader("❌ Cancelar / Remover Assinante Específico")
            assinante_remover = st.selectbox("Selecione o Cliente para Cancelar Plano:", assinaturas_df["Cliente"].tolist())
            if st.button("Remover Assinatura do Cliente", type="secondary"):
                assinaturas_df = assinaturas_df[assinaturas_df["Cliente"] != assinante_remover]
                assinaturas_df.to_csv(ARQUIVO_ASSINATURAS, index=False, encoding='utf-8')
                st.success(f"🗑️ O cliente '{assinante_remover}' foi removido do clube.")
                time.sleep(1.2)
                st.rerun()
        else:
            st.info("Nenhum assinante cadastrado.")
    with tab_ass2:
        with st.container(border=True):
            st.subheader("🪪 Check-in de Assinante")
            if not assinaturas_df.empty:
                cliente_uso = st.selectbox("Selecione o Cliente:", assinaturas_df["Cliente"].tolist())
                servico_uso = st.selectbox("Qual o procedimento?", ["Corte de Cabelo", "Fazer a Barba", "Corte + Barba"])
                lista_barbeiros_sistema = barbeiros_df["Nome"].tolist() if not barbeiros_df.empty else ["G."]
                barbeiro_atendeu = st.selectbox("Barbeiro Atendente:", lista_barbeiros_sistema)
                if st.button("💾 Validar Entrada", type="primary", use_container_width=True):
                    nova_presenca = pd.DataFrame([{"Data": datetime.now().strftime("%Y-%m-%d"), "Cliente": cliente_uso, "Serviço Usado": servico_uso, "Barbeiro Atendeu": barbeiro_atendeu}])
                    presencas_df = pd.concat([presencas_df, nova_presenca], ignore_index=True)
                    presencas_df.to_csv(ARQUIVO_PRESENCAS, index=False, encoding='utf-8')
                    st.success(f"✅ Presença registrada para {cliente_uso}.")
                    time.sleep(1.2)
                    st.rerun()
    with tab_ass3:
        st.subheader("📈 Frequência Mensal do Clube")
        if not presencas_df.empty:
            contagem_visitas = presencas_df.groupby("Cliente")["Serviço Usado"].count().reset_index()
            contagem_visitas.columns = ["Nome do Cliente Assinante", "Uso no Mês (Vezes)"]
            st.dataframe(contagem_visitas, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma presença registrada ainda.")

# ---------------- MÓDULO 3: LANÇAR GASTO ----------------
elif menu == "📉 Lançar Gasto/Despesa":
    st.header("📉 Fluxo de Saída / Gastos")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            descricao = st.text_input("Descrição do Gasto:")
            valor_gasto = st.number_input("Valor Pago (R$):", min_value=0.0, step=0.50)
        with col2:
            categoria = st.selectbox("Categoria:", ["Infraestrutura (Luz/Água/Aluguel)", "Produtos (Reposição)", "Equipamentos", "Outros"])
        if st.button("💾 Gravar Gasto", type="primary", use_container_width=True):
            if descricao != "" and valor_gasto > 0:
                novo_gasto = pd.DataFrame([{"Data": datetime.now().strftime("%Y-%m-%d"), "Descrição": descricao, "Valor (R$)": valor_gasto, "Categoria": categoria}])
                gastos_df = pd.concat([gastos_df, novo_gasto], ignore_index=True)
                gastos_df.to_csv(ARQUIVO_GASTOS, index=False, encoding='utf-8')
                st.success(f"✅ Custo registrado!")
                time.sleep(1.2)
                st.rerun()

# ---------------- MÓDULO 4: CORRIGIR LANÇAMENTOS ----------------
elif menu == "✏️ Corrigir Lançamentos":
    st.header("✏️ Central de Correções e Estornos de Caixa")
    if not vendas_df.empty:
        vendas_visivel_df = vendas_df.copy()
        vendas_visivel_df.insert(0, "ID_Lancamento", vendas_visivel_df.index)
        st.dataframe(vendas_visivel_df.sort_index(ascending=False), use_container_width=True, hide_index=True)
        st.markdown("---")
        col_ed1, col_ed2 = st.columns(2, gap="large")
        with col_ed1:
            with st.container(border=True):
                st.subheader("✏️ Editar Lançamento")
                id_selecionado = st.selectbox("Selecione o ID do lançamento:", vendas_visivel_df["ID_Lancamento"].tolist())
                linha_original = vendas_df.iloc[id_selecionado]
                lista_barbeiros_sistema = barbeiros_df["Nome"].tolist() if not barbeiros_df.empty else ["G."]
                novo_b = st.selectbox("Mudar Barbeiro para:", lista_barbeiros_sistema, index=lista_barbeiros_sistema.index(linha_original['Barbeiro']) if linha_original['Barbeiro'] in lista_barbeiros_sistema else 0)
                nova_f_pagto = st.selectbox("Mudar Forma de Pagamento:", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"], index=["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"].index(linha_original['Forma de Pagamento']))
                novo_cliente_nome = st.text_input("Nome do Cliente:", value=linha_original['Cliente'])
                if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
                    vendas_df.at[id_selecionado, 'Barbeiro'] = novo_b
                    vendas_df.at[id_selecionado, 'Forma de Pagamento'] = nova_f_pagto
                    vendas_df.at[id_selecionado, 'Cliente'] = novo_cliente_nome
                    vendas_df.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
                    st.success("✅ Informações alteradas!")
                    time.sleep(1.2)
                    st.rerun()
        with col_ed2:
            with st.container(border=True):
                st.subheader("🗑️ Apagar Lançamento")
                id_remover = st.selectbox("Selecione o ID para remover:", vendas_visivel_df["ID_Lancamento"].tolist())
                if st.button("❌ Excluir Lançamento Errado", use_container_width=True):
                    vendas_df = vendas_df.drop(id_remover).reset_index(drop=True)
                    vendas_df.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
                    st.success("🗑️ Lançamento removido do histórico!")
                    time.sleep(1.2)
                    st.rerun()
    else:
        st.info("Nenhuma venda disponível.")

# ---------------- MÓDULO 5: GERENCIAR BARBEIROS ----------------
elif menu == "👥 Cadastrar Barbeiro":
    st.header("👥 Gestão de Barbeiros da Equipe")
    col_cad1, col_cad2 = st.columns(2, gap="large")
    with col_cad1:
        with st.container(border=True):
            st.subheader("➕ Adicionar Barbeiro")
            novo_nome = st.text_input("Nome:")
            nova_comissao = st.number_input("Comissão (%):", min_value=0.0, max_value=100.0, value=50.0, step=5.0)
            if st.button("Cadastrar Barbeiro", type="primary", use_container_width=True):
                if novo_nome != "" and novo_nome not in barbeiros_df["Nome"].tolist():
                    novo_b = pd.DataFrame([{"Nome": novo_nome, "Comissão (%)": nova_comissao}])
                    barbeiros_df = pd.concat([barbeiros_df, novo_b], ignore_index=True)
                    barbeiros_df.to_csv(ARQUIVO_BARBEIROS, index=False, encoding='utf-8')
                    st.success(f"👤 Profissional '{novo_nome}' ativo!")
                    time.sleep(1.2)
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.subheader("❌ Remover Barbeiro")
            if not barbeiros_df.empty:
                barbeiro_remover = st.selectbox("Selecione para Remover:", barbeiros_df["Nome"].tolist())
                if st.button("Remover Permanentemente", use_container_width=True):
                    barbeiros_df = barbeiros_df[barbeiros_df["Nome"] != barbeiro_remover]
                    barbeiros_df.to_csv(ARQUIVO_BARBEIROS, index=False, encoding='utf-8')
                    st.success(f"🗑️ Profissional removido.")
                    time.sleep(1.2)
                    st.rerun()
    with col_cad2:
        st.subheader("Profissionais Ativos")
        st.dataframe(barbeiros_df, use_container_width=True, hide_index=True)

# ---------------- MÓDULO 6: ESTOQUE & SERVIÇOS ----------------
elif menu == "📦 Estoque & Serviços":
    st.header("📦 Monitor do Estoque Conveniência e Serviços")
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    produtos_calculados = produtos_df.copy()
    qtd_vendida_map = vendas_df[vendas_df["Tipo"] == "Produto"].groupby("Item")["Quantidade"].sum().to_dict()
    produtos_calculados["Quantidade Vendida"] = produtos_calculados["Nome do Produto"].map(qtd_vendida_map).fillna(0).astype(int)
    produtos_calculados["Estoque Atual"] = produtos_calculados["Estoque Inicial"] - produtos_calculados["Quantidade Vendida"]
    with st.container(border=True):
        st.subheader("📦 Nível de Prateleira (Produtos)")
        st.dataframe(produtos_calculados, use_container_width=True, hide_index=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader("💈 Catálogo Vigente de Serviços")
        st.dataframe(servicos_df, use_container_width=True, hide_index=True)

# ---------------- MÓDULO 7: GERENCIAR CATÁLOGO ----------------
elif menu == "⚙️ Gerenciar Catálogo":
    st.header("⚙️ Modificação de Catálogo e Preços")
    aba_serv, aba_prod = st.tabs(["💈 Serviços", "📦 Produtos/Bebidas"])
    with aba_serv:
        with st.container(border=True):
            st.subheader("Adicionar Novo Serviço")
            s_nome = st.text_input("Nome do Serviço:")
            s_preco = st.number_input("Preço (R$):", min_value=0.0, value=20.0, step=5.0)
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
            st.subheader("Mudar Preço Existente")
            servico_editar = st.selectbox("Escolha o Serviço:", servicos_df["Nome do Serviço"].tolist())
            novo_preco_s = st.number_input("Modificar Valor:", min_value=0.0, value=float(servicos_df[servicos_df["Nome do Serviço"] == servico_editar]["Preço (R$)"].values[0]))
            if st.button("Atualizar Valor", type="primary"):
                servicos_df.loc[servicos_df["Nome do Serviço"] == servico_editar, "Preço (R$)"] = novo_preco_s
                servicos_df.to_csv(ARQUIVO_SERVICOS, index=False, encoding='utf-8')
                st.success("🎉 Preço atualizado!")
                time.sleep(1.2)
                st.rerun()
    with aba_prod:
        with st.container(border=True):
            st.subheader("Cadastrar Novo Produto")
            col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
            with col_p1: p_nome = st.text_input("Nome do Produto:")
            with col_p2: p_venda = st.number_input("Preço Venda:", min_value=0.0, value=10.0)
            with col_p3: p_custo = st.number_input("Preço Custo:", min_value=0.0, value=5.0)
            with col_p4: p_estoque = st.number_input("Estoque:", min_value=0, value=10)
            with col_p5: p_comis = st.number_input("Comissão R$:", min_value=0.0, value=0.0)
            if st.button("Salvar Produto", type="primary", use_container_width=True):
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
            st.subheader("Editar Produto Existente")
            prod_editar = st.selectbox("Selecione o Produto:", produtos_df["Nome do Produto"].tolist())
            col_ed1, col_ed2, col_ed3, col_ed4 = st.columns(4)
            item_linha = produtos_df[produtos_df["Nome do Produto"] == prod_editar]
            with col_ed1: ed_venda = st.number_input("Preço Venda:", value=float(item_linha["Preço de Venda"].values[0]))
            with col_ed2: ed_custo = st.number_input("Preço Custo:", value=float(item_linha["Preço de Custo"].values[0]))
            with col_ed3: ed_estoque = st.number_input("Estoque Inicial:", value=int(item_linha["Estoque Inicial"].values[0]))
            with col_ed4: ed_comis = st.number_input("Comissão Fixa R$:", value=float(item_linha["Comissão Barbeiro (R$)"].values[0]))
            if st.button("Salvar Modificações", type="primary", use_container_width=True):
                produtos_df.loc[produtos_df["Nome do Produto"] == prod_editar, ["Preço de Venda", "Preço de Custo", "Estoque Inicial", "Comissão Barbeiro (R$)"]] = [ed_venda, ed_custo, ed_estoque, ed_comis]
                produtos_df.to_csv(ARQUIVO_PRODUTOS, index=False, encoding='utf-8')
                st.success("🔥 Informações updated!")
                time.sleep(1.2)
                st.rerun()

# ---------------- MÓDULO 8: GERENCIAR USUÁRIOS E PERMISSÕES ----------------
elif menu == "👤 Gerenciar Usuários":
    st.header("👤 Gerenciamento de Usuários e Níveis de Acesso")
    st.write("Crie perfis para gerentes ou barbeiros e marque quais abas eles podem utilizar.")
    col_u1, col_u2 = st.columns(2, gap="large")
    with col_u1:
        with st.container(border=True):
            st.subheader("➕ Criar Novo Perfil de Acesso")
            novo_usr = st.text_input("Nome do Usuário de Login (Sem espaços):").strip().lower()
            nova_pwd = st.text_input("Definir Senha de Acesso:", type="password")
            st.write("**Marque quais telas este usuário poderá ver:**")
            p_venda = st.checkbox("💸 Abrir Comanda (Vendas)", value=True)
            p_estoque = st.checkbox("📦 Estoque & Serviços", value=True)
            p_clube = st.checkbox("💳 Clube de Assinaturas")
            p_gastos = st.checkbox("📉 Lançar Gasto/Despesa")
            p_correcao = st.checkbox("✏️ Corrigir Lançamentos")
            p_barbeiro = st.checkbox("👥 Cadastrar Barbeiro")
            p_catalogo = st.checkbox("⚙️ Gerenciar Catálogo")
            p_relatorios = st.checkbox("📊 Painel de Relatórios")
            if st.button("💾 Gravar e Liberar Usuário", type="primary", use_container_width=True):
                if novo_usr != "" and nova_pwd != "":
                    if novo_usr not in usuarios_df["Usuario"].str.lower().tolist():
                        lista_p = []
                        if p_venda: lista_p.append("💸 Abrir Comanda (Vendas)")
                        if p_estoque: lista_p.append("📦 Estoque & Serviços")
                        if p_clube: lista_p.append("💳 Clube de Assinaturas")
                        if p_gastos: lista_p.append("📉 Lançar Gasto/Despesa")
                        if p_correcao: lista_p.append("✏️ Corrigir Lançamentos")
                        if p_barbeiro: lista_p.append("👥 Cadastrar Barbeiro")
                        if p_catalogo: lista_p.append("⚙️ Gerenciar Catálogo")
                        if p_relatorios: lista_p.append("📊 Painel de Relatórios")
                        perm_formatada = "|".join(lista_p)
                        novo_u_df = pd.DataFrame([{"Usuario": novo_usr, "Senha": nova_pwd, "Permissoes": perm_formatada}])
                        usuarios_df = pd.concat([usuarios_df, novo_u_df], ignore_index=True)
                        usuarios_df.to_csv(ARQUIVO_USUARIOS, index=False, encoding='utf-8')
                        st.success(f"🎉 Login para '{novo_usr}' criado!")
                        time.sleep(1.2)
                        st.rerun()
                    else:
                        st.error("Esse nome de usuário já está sendo usado.")
                else:
                    st.error("Preencha o usuário e a senha.")
    with col_u2:
        st.subheader("📋 Usuários Cadastrados no Sistema")
        st.dataframe(usuarios_df["Usuario"], use_container_width=True, hide_index=True)
        st.markdown("---")
        st.subheader("🗑️ Excluir Usuário")
        usuarios_excluir_lista = [u for u in usuarios_df["Usuario"].tolist() if u.lower() != "admin"]
        if usuarios_excluir_lista:
            usr_remover = st.selectbox("Selecione qual usuário remover da barbearia:", usuarios_excluir_lista)
            if st.button("Bloquear e Excluir Usuário", use_container_width=True):
                usuarios_df = usuarios_df[usuarios_df["Usuario"] != usr_remover]
                usuarios_df.to_csv(ARQUIVO_USUARIOS, index=False, encoding='utf-8')
                st.success(f"Usuário '{usr_remover}' removido!")
                time.sleep(1.2)
                st.rerun()
        else:
            st.info("Nenhum usuário secundário criado ainda.")

# ---------------- MÓDULO 9: PAINEL DE RELATÓRIOS ----------------
elif menu == "📊 Painel de Relatórios":
    st.header("📊 Dashboard Financeiro - O Chefão")
    vendas_df["Valor Total"] = pd.to_numeric(vendas_df["Valor Total"], errors='coerce').fillna(0)
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    gastos_df["Valor (R$)"] = pd.to_numeric(gastos_df["Valor (R$)"], errors='coerce').fillna(0)
    faturamento = vendas_df["Valor Total"].sum()
    total_gastos = gastos_df["Valor (R$)"].sum()
    lucro_liquido = faturamento - total_gastos
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("💰 FATURAMENTO BRUTO", f"R$ {faturamento:.2f}")
    with c2: st.metric("📉 TOTAL DE GASTOS", f"R$ {total_gastos:.2f}")
    with c3: st.metric("🔥 LUCRO LÍQUIDO REAL", f"R$ {lucro_liquido:.2f}")
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader("💸 Tabela Unificada de Comissões Semanal")
        if not barbeiros_df.empty:
            relatorio_comissao = []
            mapa_comissao_produto = produtos_df.set_index("Nome do Produto")["Comissão Barbeiro (R$)"].to_dict()
            for _, b in barbeiros_df.iterrows():
                nome_b = b["Nome"]
                porcentagem_servico = b["Comissão (%)"]
                vendas_do_barbeiro = vendas_df[vendas_df["Barbeiro"] == nome_b]
                servicos_b = vendas_do_barbeiro[vendas_do_barbeiro["Tipo"] == "Serviço"]
                faturamento_servicos = servicos_b["Valor Total"].sum()
                total_cortes = servicos_b["Quantidade"].sum()
                valor_comissao_servico = faturamento_servicos * (porcentagem_servico / 100.0)
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
    st.markdown("<br>", unsafe_allow_html=True)
    col_g1, col_g2 = st.columns(2, gap="large")
    with col_g1:
        st.subheader("📅 Faturamento Diário")
        if not vendas_df.empty: st.line_chart(vendas_df.groupby("Data")["Valor Total"].sum())
    with col_g2:
        st.subheader("💰 Divisão Balcão (Serviços vs Produtos)")
        if not vendas_df.empty: st.bar_chart(vendas_df.groupby("Tipo")["Valor Total"].sum())
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Histórico de Vendas", "📉 Histórico de Gastos"])
    with tab1: st.dataframe(vendas_df.sort_index(ascending=False), use_container_width=True, hide_index=True)
    with tab2: st.dataframe(gastos_df.sort_index(ascending=False), use_container_width=True, hide_index=True)

# ---------------- MÓDULO 10: CONFIGURAÇÕES ----------------
elif menu == "⚙️ Configurações":
    st.header("Configurações Globais")
    with st.container(border=True):
        st.subheader("💳 Limpar Apenas o Clube de Assinaturas")
        if st.button("🚨 Zerar Clientes de Assinatura", type="primary", use_container_width=True):
            pd.DataFrame(columns=["Cliente", "Plano", "Data Inicio", "Data Vencimento", "Valor Mensal"]).to_csv(ARQUIVO_ASSINATURAS, index=False, encoding='utf-8')
            pd.DataFrame(columns=["Data", "Cliente", "Serviço Usado", "Barbeiro Atendeu"]).to_csv(ARQUIVO_PRESENCAS, index=False, encoding='utf-8')
            st.success("Clube resetado!")
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader("💰 Limpar Caixa Geral (Vendas)")
        if st.button("🚨 Limpar Todas as Vendas e Zerar Caixa", use_container_width=True):
            pd.DataFrame(columns=["Data", "Item", "Tipo", "Quantidade", "Valor Total", "Forma de Pagamento", "Barbeiro", "Cliente"]).to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
            st.success("Caixa redefinido!")
            st.rerun()
