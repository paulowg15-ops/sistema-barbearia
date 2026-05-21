import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import zipfile
import io
import base64
from fpdf import FPDF

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
ARQUIVO_CONSUMO_INTERNO = "consumo_interno.csv"
ARQUIVO_FECHAMENTOS = "fechamentos.csv"

# Lista oficial para o Backup ZIP
TODOS_ARQUIVOS_BACKUP = {
    "vendas.csv": ARQUIVO_VENDAS,
    "gastos.csv": ARQUIVO_GASTOS,
    "barbeiros.csv": ARQUIVO_BARBEIROS,
    "assinaturas.csv": ARQUIVO_ASSINATURAS,
    "presencas.csv": ARQUIVO_PRESENCAS,
    "consumo_interno.csv": ARQUIVO_CONSUMO_INTERNO,
    "usuarios.csv": ARQUIVO_USUARIOS,
    "fechamentos.csv": ARQUIVO_FECHAMENTOS
}

def inicializar_banco_de_dados():
    if not os.path.exists(ARQUIVO_SERVICOS):
        pd.DataFrame([
            {"ID": 1, "Nome do Serviço": "Corte Social", "Preço (R$)": 35.0},
            {"ID": 2, "Nome do Serviço": "Barba Completa", "Preço (R$)": 25.0},
            {"ID": 3, "Nome do Serviço": "Combo (Corte + Barba)", "Preço (R$)": 55.0}
        ]).to_csv(ARQUIVO_SERVICOS, index=False, encoding='utf-8')

    if not os.path.exists(ARQUIVO_PRODUTOS):
        pd.DataFrame([
            {"ID": 1, "Nome do Produto": "Pomada Modeladora", "Preço de Venda": 40.0, "Preço de Custo": 20.0, "Estoque Inicial": 10, "Comissão Barbeiro (R$)": 5.0},
            {"ID": 2, "Nome do Produto": "Cerveja Long Neck", "Preço de Venda": 8.0, "Preço de Custo": 4.0, "Estoque Inicial": 24, "Comissão Barbeiro (R$)": 0.0}
        ]).to_csv(ARQUIVO_PRODUTOS, index=False, encoding='utf-8')

    for arquivo in TODOS_ARQUIVOS_BACKUP.values():
        if not os.path.exists(arquivo):
            if arquivo == ARQUIVO_USUARIOS:
                pd.DataFrame([{"Usuario": "admin", "Senha": "barba123", "Permissoes": "TODAS"}]).to_csv(arquivo, index=False, encoding='utf-8')
            elif arquivo == ARQUIVO_BARBEIROS:
                pd.DataFrame([{"Nome": "G.", "Comissão (%)": 50.0}]).to_csv(arquivo, index=False, encoding='utf-8')
            elif arquivo == ARQUIVO_FECHAMENTOS:
                pd.DataFrame(columns=["Data", "Usuario", "Dinheiro Real", "Pix Real", "Cartao Real", "Total Real", "Total Sistema", "Diferenca", "Status", "Observacoes"]).to_csv(arquivo, index=False, encoding='utf-8')
            else:
                pd.DataFrame().to_csv(arquivo, index=False, encoding='utf-8')

inicializar_banco_de_dados()

usuarios_df = pd.read_csv(ARQUIVO_USUARIOS, encoding='utf-8')

PERMISSOES_MASTER = ["💸 Abrir Comanda (Vendas)", "💳 Clube de Assinaturas", "📉 Lançar Gasto/Despesa", "✏️ Corrigir Lançamentos", "🔒 Fechamento de Dia", "👥 Cadastrar Barbeiro", "📦 Estoque & Serviços", "⚙️ Gerenciar Catálogo", "👤 Gerenciar Usuários", "📊 Painel de Relatórios", "📄 Emitir Relatórios", "💾 Backup do Sistema", "⚙️ Configurações"]
PERMISSOES_PADRAO = ["💸 Abrir Comanda (Vendas)", "📦 Estoque & Serviços"]

# --- SISTEMA DE LOGIN MULTI-USUÁRIO (TOKEN VIA URL) ---
def gerar_token(usuario):
    validade = (datetime.now() + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")
    texto = f"{usuario}|{validade}"
    return base64.b64encode(texto.encode('utf-8')).decode('utf-8')

def validar_token(token):
    try:
        texto = base64.b64decode(token.encode('utf-8')).decode('utf-8')
        usuario, validade_str = texto.split("|")
        validade = datetime.strptime(validade_str, "%Y-%m-%d %H:%M:%S")
        if datetime.now() <= validade:
            return usuario
    except: pass
    return None

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["perfil"] = None
    st.session_state["permissoes_usuario"] = PERMISSOES_PADRAO
    st.session_state["carrinho_comanda"] = []

# Checagem automática do F5
if not st.session_state["autenticado"] and "token" in st.query_params:
    usr_decodificado = validar_token(st.query_params["token"])
    if usr_decodificado:
        usuarios_df["Usuario_Lower"] = usuarios_df["Usuario"].str.strip().str.lower()
        u_linha = usuarios_df[usuarios_df["Usuario_Lower"] == usr_decodificado.strip().lower()]
        if not u_linha.empty:
            st.session_state["autenticado"] = True
            st.session_state["perfil"] = usr_decodificado
            perm_string = u_linha.iloc[0]["Permissoes"]
            st.session_state["permissoes_usuario"] = PERMISSOES_MASTER if perm_string == "TODAS" else perm_string.split("|")

# --- TELA DE LOGIN ---
if not st.session_state["autenticado"]:
    st.title("💈 O Chefão Barbearia e Conveniência")
    st.write("Entre com suas credenciais para acessar o sistema")
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
                    st.query_params["token"] = gerar_token(input_usuario)
                    perm_string = usuario_valido.iloc[0]["Permissoes"]
                    st.session_state["permissoes_usuario"] = PERMISSOES_MASTER if perm_string == "TODAS" else perm_string.split("|")
                    st.rerun()
                else: st.error("Usuário ou senha incorretos!")
    st.stop()

# Carregar tabelas completas
servicos_df = pd.read_csv(ARQUIVO_SERVICOS, encoding='utf-8')
produtos_df = pd.read_csv(ARQUIVO_PRODUTOS, encoding='utf-8')
vendas_df = pd.read_csv(ARQUIVO_VENDAS, encoding='utf-8').dropna(how='all')
gastos_df = pd.read_csv(ARQUIVO_GASTOS, encoding='utf-8').dropna(how='all')
barbeiros_df = pd.read_csv(ARQUIVO_BARBEIROS, encoding='utf-8').dropna(how='all')
assinaturas_df = pd.read_csv(ARQUIVO_ASSINATURAS, encoding='utf-8').dropna(how='all')
presencas_df = pd.read_csv(ARQUIVO_PRESENCAS, encoding='utf-8').dropna(how='all')
consumo_interno_df = pd.read_csv(ARQUIVO_CONSUMO_INTERNO, encoding='utf-8').dropna(how='all')
fechamentos_df = pd.read_csv(ARQUIVO_FECHAMENTOS, encoding='utf-8').dropna(how='all')

# --- CONFIGURAÇÃO DA BARRA LATERAL ---
st.sidebar.title("✂️ O Chefão")
st.sidebar.write(f"Conectado como: **{st.session_state['perfil'].upper()}**")
st.sidebar.markdown("---")
menus_validos = st.session_state["permissoes_usuario"] if st.session_state["permissoes_usuario"] else PERMISSOES_PADRAO
menu = st.sidebar.radio("Navegação:", menus_validos)
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Sair com Segurança", use_container_width=True):
    st.session_state["autenticado"] = False
    st.session_state["perfil"] = None
    st.session_state["permissoes_usuario"] = []
    st.session_state["carrinho_comanda"] = []
    st.query_params.clear()
    st.rerun()

# --- CLASSE AUXILIAR DO PDF ---
class PDFRelatorio(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "O CHEFAO BARBEARIA E CONVENIENCIA", ln=1, align="C")
        self.set_font("Arial", "I", 10)
        self.cell(0, 5, "Relatorio Oficial de Movimentacao de Caixa e Auditoria", ln=1, align="C")
        self.ln(5)
        self.line(10, 26, 200, 26)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

# ---------------- MÓDULO 1: COMANDA ELETRÔNICA (ATUALIZADO COM DATA RETROATIVA PARA ADMIN) ----------------
if menu == "💸 Abrir Comanda (Vendas)":
    st.header("📋 Caixa e Comanda Eletrônica - O Chefão")
    col_com1, col_com2 = st.columns([1, 1], gap="large")
    with col_com1:
        with st.container(border=True):
            st.subheader("➕ Adicionar Item")
            tipo = st.selectbox("Selecione a Categoria:", ["Serviço (Corte/Barba)", "Produto (Bebida/Pomada)"])
            lista_itens = servicos_df["Nome do Serviço"].tolist() if tipo == "Serviço (Corte/Barba)" else produtos_df["Nome do Produto"].tolist()
            tabela_ref = servicos_df if tipo == "Serviço (Corte/Barba)" else produtos_df
            nome_col_preco = "Preço (R$)" if tipo == "Serviço (Corte/Barba)" else "Preço de Venda"
            categoria_venda = "Serviço" if tipo == "Serviço (Corte/Barba)" else "Produto"
            item_selecionado = st.selectbox("Selecione o Item do Catálogo:", lista_itens)
            qtd = st.number_input("Quantidade:", min_value=1, value=1, step=1)
            preco_unitario = tabela_ref[tabela_ref.iloc[:, 1] == item_selecionado][nome_col_preco].values[0]
            subtotal_item = float(preco_unitario) * qtd
            st.write(f"**Subtotal do item:** R$ {subtotal_item:.2f}")
            if st.button("➕ Inserir na Comanda", use_container_width=True):
                st.session_state["carrinho_comanda"].append({"Item": item_selecionado, "Tipo": categoria_venda, "Quantidade": qtd, "Valor Total": subtotal_item})
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
                
                st.subheader("🗑️ Remover Item Incorreto")
                lista_nomes_carrinho = [f"{i} - {item['Item']} ({item['Tipo']})" for i, item in enumerate(st.session_state["carrinho_comanda"])]
                item_remover_index_str = st.selectbox("Selecione o item para retirar da lista:", lista_nomes_carrinho)
                if st.button("❌ Remover Item Selecionado", use_container_width=True):
                    index_remover = int(item_remover_index_str.split(" - ")[0])
                    item_removido_nome = st.session_state["carrinho_comanda"].pop(index_remover)
                    st.toast(f"'{item_removido_nome['Item']}' removido!")
                    time.sleep(0.5)
                    st.rerun()
                
                st.markdown("---")
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    forma_pagamento = st.selectbox("Forma de Recebimento:", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
                    lista_barbeiros_sistema = barbeiros_df["Nome"].tolist() if not barbeiros_df.empty else ["G."]
                    barbeiro_venda = st.selectbox("Barbeiro Executor:", lista_barbeiros_sistema)
                with c_f2: 
                    cliente = st.text_input("Identificação do Cliente:", value="Avulso")
                    
                    # TRAVA EXCLUSIVA OPÇÃO 2: Apenas admin altera a data, gerente fica fixo em hoje
                    if st.session_state["perfil"] == "admin":
                        data_venda_dt = st.date_input("📅 Data do Lançamento:", datetime.now())
                        data_final_comanda = data_venda_dt.strftime("%Y-%m-%d")
                    else:
                        data_final_comanda = datetime.now().strftime("%Y-%m-%d")

                if st.button("🚀 Finalizar Conta e Registrar", type="primary", use_container_width=True):
                    novas_linhas = []
                    for item_c in st.session_state["carrinho_comanda"]:
                        item_c["Data"] = data_final_comanda
                        item_c["Forma de Pagamento"] = forma_pagamento
                        item_c["Barbeiro"] = barbeiro_venda
                        item_c["Cliente"] = cliente
                        novas_linhas.append(item_c)
                    vendas_df = pd.concat([vendas_df, pd.DataFrame(novas_linhas)], ignore_index=True)
                    vendas_df.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
                    st.session_state["carrinho_comanda"] = []
                    st.success(f"✅ Venda de R$ {valor_total_comanda:.2f} lançada para o dia {data_final_comanda}!")
                    time.sleep(1.2)
                    st.rerun()
                if st.button("🗑️ Esvaziar Comanda Completa", use_container_width=True):
                    st.session_state["carrinho_comanda"] = []
                    st.rerun()
            else: st.info("A comanda eletrônica está limpa.")

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
            with col_as3: forma_pago_ass = st.selectbox("Canal de Recebimento:", ["Pix", "Dinheiro", "Cartão"])
            if st.button("🔥 Ativar Plano", type="primary", use_container_width=True):
                if nome_ass != "":
                    venc_calc = (data_pago + timedelta(days=30)).strftime("%Y-%m-%d")
                    nova_ass = pd.DataFrame([{"Cliente": nome_ass, "Plano": plano_ass, "Data Inicio": data_pago.strftime("%Y-%m-%d"), "Data Vencimento": venc_calc, "Valor Mensal": valor_ass}])
                    assinaturas_df = pd.concat([assinaturas_df, nova_ass], ignore_index=True)
                    assinaturas_df.to_csv(ARQUIVO_ASSINATURAS, index=False, encoding='utf-8')
                    venda_ass = pd.DataFrame([{"Data": data_pago.strftime("%Y-%m-%d"), "Item": f"Clube: {plano_ass}", "Tipo": "Serviço", "Quantidade": 1, "Valor Total": valor_ass, "Forma de Pagamento": forma_pago_ass, "Barbeiro": "ADMIN", "Cliente": nome_ass}])
                    vendas_df = pd.concat([vendas_df, venda_ass], ignore_index=True)
                    vendas_df.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
                    st.success(f"✅ Assinatura activa!")
                    time.sleep(1.2)
                    st.rerun()
        if not assinaturas_df.empty:
            data_hoje = datetime.now().date()
            for idx, r in assinaturas_df.iterrows():
                venc_date = datetime.strptime(r["Data Vencimento"], "%Y-%m-%d").date()
                dias_restantes = (venc_date - data_hoje).days
                if dias_restantes < 0: st.error(f"🔴 **{r['Cliente']}** | Venceu em: {r['Data Vencimento']} (Bloqueado!)")
                elif dias_restantes <= 5: st.warning(f"⚠️ **{r['Cliente']}** | Vence em: {r['Data Vencimento']} (Restam {dias_restantes} dias!)")
                else: st.info(f"🟢 **{r['Cliente']}** | Vencimento: {r['Data Vencimento']} ({dias_restantes} dias)")
            st.markdown("---")
            assinante_remover = st.selectbox("Selecione o Cliente para Cancelar Plano:", assinaturas_df["Cliente"].tolist())
            if st.session_state["perfil"] == "admin":
                if st.button("Remover Assinatura do Cliente", type="secondary"):
                    assinaturas_df = assinaturas_df[assinaturas_df["Cliente"] != assinante_remover]
                    assinaturas_df.to_csv(ARQUIVO_ASSINATURAS, index=False, encoding='utf-8')
                    st.success("🗑️ Cliente removido.")
                    time.sleep(1.2)
                    st.rerun()
            else: st.error("🚫 Apenas o admin pode cancelar assinaturas.")
    with tab_ass2:
        with st.container(border=True):
            if not assinaturas_df.empty:
                cliente_uso = st.selectbox("Selecione o Cliente:", assinaturas_df["Cliente"].tolist())
                servico_uso = st.selectbox("Qual o procedimento?", ["Corte de Cabelo", "Fazer a Barba", "Corte + Barba"])
                lista_barbeiros_sistema = barbeiros_df["Nome"].tolist() if not barbeiros_df.empty else ["G."]
                barbeiro_atendeu = st.selectbox("Barbeiro Atendente:", lista_barbeiros_sistema)
                if st.button("💾 Validar Entrada", type="primary", use_container_width=True):
                    nova_presenca = pd.DataFrame([{"Data": datetime.now().strftime("%Y-%m-%d"), "Cliente": cliente_uso, "Serviço Usado": servico_uso, "Barbeiro Atendeu": barbeiro_atendeu}])
                    presencas_df = pd.concat([presencas_df, nova_presenca], ignore_index=True)
                    presencas_df.to_csv(ARQUIVO_PRESENCAS, index=False, encoding='utf-8')
                    st.success("✅ Presença registrada!")
                    time.sleep(1.2)
                    st.rerun()
    with tab_ass3:
        if not presencas_df.empty:
            contagem_visitas = presencas_df.groupby("Cliente")["Serviço Usado"].count().reset_index()
            st.dataframe(contagem_visitas, use_container_width=True, hide_index=True)

# ---------------- MÓDULO 3: LANÇAR GASTO ----------------
elif menu == "📉 Lançar Gasto/Despesa":
    st.header("📉 Fluxo de Saída / Gastos")
    with st.container(border=True):
        descricao = st.text_input("Descrição do Gasto:")
        valor_gasto = st.number_input("Valor Pago (R$):", min_value=0.0, step=0.50)
        categoria = st.selectbox("Categoria:", ["Infraestrutura (Luz/Água/Aluguel)", "Produtos (Reposição)", "Equipamentos", "Outros"])
        if st.button("💾 Gravar Gasto", type="primary", use_container_width=True):
            if descricao != "" and valor_gasto > 0:
                novo_gasto = pd.DataFrame([{"Data": datetime.now().strftime("%Y-%m-%d"), "Descrição": descricao, "Valor (R$)": valor_gasto, "Categoria": categoria}])
                gastos_df = pd.concat([gastos_df, novo_gasto], ignore_index=True)
                gastos_df.to_csv(ARQUIVO_GASTOS, index=False, encoding='utf-8')
                st.success("✅ Custo registrado!")
                time.sleep(1.2)
                st.rerun()

# ---------------- MÓDULO 4: CORRIGIR LANÇAMENTOS ----------------
elif menu == "✏️ Corrigir Lançamentos":
    st.header("✏️ Central de Correções e Estornos")
    tab_corr_vendas, tab_corr_fechamentos = st.tabs(["🛒 Corrigir Comandas de Caixa", "🔒 Auditar Fechamentos Diários"])
    with tab_corr_vendas:
        if not vendas_df.empty:
            vendas_visivel_df = vendas_df.copy()
            vendas_visivel_df.insert(0, "ID_Lancamento", vendas_visivel_df.index)
            st.dataframe(vendas_visivel_df.sort_index(ascending=False), use_container_width=True, hide_index=True)
            col_ed1, col_ed2 = st.columns(2, gap="large")
            with col_ed1:
                with st.container(border=True):
                    id_selecionado = st.selectbox("Selecione o ID do lançamento:", vendas_visivel_df["ID_Lancamento"].tolist())
                    linha_original = vendas_df.iloc[id_selecionado]
                    lista_barbeiros_sistema = barbeiros_df["Nome"].tolist() if not barbeiros_df.empty else ["G."]
                    novo_b = st.selectbox("Mudar Barbeiro:", lista_barbeiros_sistema, index=lista_barbeiros_sistema.index(linha_original['Barbeiro']) if linha_original['Barbeiro'] in lista_barbeiros_sistema else 0)
                    nova_f_pagto = st.selectbox("Mudar Pagamento:", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"], index=["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"].index(linha_original['Forma de Pagamento']))
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
                    id_remover = st.selectbox("Selecione o ID para remover:", vendas_visivel_df["ID_Lancamento"].tolist())
                    if st.session_state["perfil"] == "admin":
                        if st.button("❌ Excluir Lançamento Errado", use_container_width=True):
                            vendas_df = vendas_df.drop(id_remover).reset_index(drop=True)
                            vendas_df.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
                            st.success("🗑️ Removido!")
                            time.sleep(1.2)
                            st.rerun()
                    else: st.error("🚫 Acesso Negado: Apenas o Administrador pode apagar vendas.")
        else: st.info("Nenhuma venda disponível.")

    with tab_corr_fechamentos:
        st.subheader("🗑️ Excluir Fechamento Diário Incorreto")
        if st.session_state["perfil"] == "admin":
            if not fechamentos_df.empty:
                fech_visivel_df = fechamentos_df.copy()
                fech_visivel_df.insert(0, "ID_Fechamento", fech_visivel_df.index)
                st.dataframe(fech_visivel_df.sort_index(ascending=False), use_container_width=True, hide_index=True)
                id_fech_remover = st.selectbox("Selecione o ID para remover:", fech_visivel_df["ID_Fechamento"].tolist())
                if st.button("❌ Excluir Fechamento Selecionado", use_container_width=True):
                    fechamentos_df = fechamentos_df.drop(id_fech_remover).reset_index(drop=True)
                    fechamentos_df.to_csv(ARQUIVO_FECHAMENTOS, index=False, encoding='utf-8')
                    st.success("🗑️ Fechamento removido do histórico!")
                    time.sleep(1.2)
                    st.rerun()
            else: st.info("Nenhum fechamento registrado no sistema.")
        else: st.error("🚫 Acesso Negado: Apenas o Admin pode anular um fechamento.")

# ---------------- MÓDULO 5: FECHAMENTO DE DIA ----------------
elif menu == "🔒 Fechamento de Dia":
    st.header("🔒 Fechamento de Caixa Diário - Auditoria")
    tab_f_1, tab_f_2 = st.tabs(["📝 Realizar Fechamento de Hoje", "📋 Histórico de Auditoria"])
    data_hoje_f = datetime.now().strftime("%Y-%m-%d")
    with tab_f_1:
        vendas_df["Valor Total"] = pd.to_numeric(vendas_df["Valor Total"], errors='coerce').fillna(0)
        vendas_hoje = vendas_df[vendas_df["Data"] == data_hoje_f]
        total_sistema_hoje = vendas_hoje["Valor Total"].sum()
        col_fe1, col_fe2 = st.columns(2, gap="large")
        with col_fe1:
            with st.container(border=True):
                real_dinheiro = st.number_input("Dinheiro Físico na Gaveta (R$):", min_value=0.0, step=5.0)
                real_pix = st.number_input("Pix (R$):", min_value=0.0, step=5.0)
                real_cartao = st.number_input("Cartões (R$):", min_value=0.0, step=5.0)
                obs_fechamento = st.text_area("Observações:", placeholder="Ex: Faltou troco...")
                total_real_calculado = real_dinheiro + real_pix + real_cartao
                diferenca_caixa = total_real_calculado - total_sistema_hoje
                if diferenca_caixa == 0: status_caixa = "🟢 Bateu Perfeitamente"
                elif diferenca_caixa > 0: status_caixa = f"🔵 Sobrou R$ {diferenca_caixa:.2f}"
                else: status_caixa = f"🔴 Quebra de Caixa (Faltou R$ {abs(diferenca_caixa):.2f})"
                if st.button("🔒 Confirmar Fechamento", type="primary", use_container_width=True):
                    novo_f_df = pd.DataFrame([{"Data": data_hoje_f, "Usuario": st.session_state["perfil"], "Dinheiro Real": real_dinheiro, "Pix Real": real_pix, "Cartao Real": real_cartao, "Total Real": total_real_calculado, "Total Sistema": total_sistema_hoje, "Diferenca": diferenca_caixa, "Status": status_caixa, "Observacoes": obs_fechamento}])
                    fechamentos_df = pd.concat([fechamentos_df, novo_f_df], ignore_index=True)
                    fechamentos_df.to_csv(ARQUIVO_FECHAMENTOS, index=False, encoding='utf-8')
                    st.success("🔒 Caixa fechado!")
                    time.sleep(1.2)
                    st.rerun()
        with col_fe2:
            with st.container(border=True):
                st.metric("📱 Esperado no Sistema", f"R$ {total_sistema_hoje:.2f}")
                st.metric("💵 Contado na Realidade", f"R$ {total_real_calculado:.2f}")
                st.metric("📊 Status", status_caixa)
    with tab_f_2:
        if not fechamentos_df.empty: st.dataframe(fechamentos_df.sort_index(ascending=False), use_container_width=True, hide_index=True)

# ---------------- MÓDULO 6: GERENCIAR BARBEIROS ----------------
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
                    st.success("👤 Profissional ativo!")
                    time.sleep(1.2)
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            if not barbeiros_df.empty:
                barbeiro_remover = st.selectbox("Selecione para Remover:", barbeiros_df["Nome"].tolist())
                if st.session_state["perfil"] == "admin":
                    if st.button("Remover Permanentemente", use_container_width=True):
                        barbeiros_df = barbeiros_df[barbeiros_df["Nome"] != barbeiro_remover]
                        barbeiros_df.to_csv(ARQUIVO_BARBEIROS, index=False, encoding='utf-8')
                        st.success("🗑️ Removido.")
                        time.sleep(1.2)
                        st.rerun()
                else: st.error("🚫 Apenas o admin pode demitir/remover um profissional.")
    with col_cad2: st.dataframe(barbeiros_df, use_container_width=True, hide_index=True)

# ---------------- MÓDULO 7: ESTOQUE & SERVIÇOS ----------------
elif menu == "📦 Estoque & Serviços":
    st.header("📦 Monitor do Estoque e Serviços")
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    produtos_calculados = produtos_df.copy()
    qtd_vendida_map = vendas_df[vendas_df["Tipo"] == "Produto"].groupby("Item")["Quantidade"].sum().to_dict()
    qtd_consumo_map = consumo_interno_df.groupby("Item")["Quantidade"].sum().to_dict()
    produtos_calculados["Quantidade Vendida"] = produtos_calculados["Nome do Produto"].map(qtd_vendida_map).fillna(0).astype(int)
    produtos_calculados["Consumo Staff"] = produtos_calculados["Nome do Produto"].map(qtd_consumo_map).fillna(0).astype(int)
    produtos_calculados["Estoque Atual"] = produtos_calculados["Estoque Inicial"] - produtos_calculados["Quantidade Vendida"] - produtos_calculados["Consumo Staff"]
    st.dataframe(produtos_calculados, use_container_width=True, hide_index=True)

# ---------------- MÓDULO 8: GERENCIAR CATÁLOGO ----------------
elif menu == "⚙️ Gerenciar Catálogo":
    st.header("⚙️ Modificação de Catálogo e Preços")
    aba_serv, aba_prod = st.tabs(["💈 Serviços", "📦 Produtos/Bebidas"])
    with aba_serv:
        col_s_1, col_s_2 = st.columns(2, gap="large")
        with col_s_1:
            with st.container(border=True):
                st.subheader("Adicionar Novo Serviço")
                s_nome = st.text_input("Nome do Serviço:")
                s_preco = st.number_input("Preço (R$):", min_value=0.0, value=20.0, step=5.0)
                if st.button("Criar Serviço", type="primary", use_container_width=True):
                    if s_nome != "":
                        novo_id = int(servicos_df["ID"].max() + 1) if not servicos_df.empty else 1
                        novo_s = pd.DataFrame([{"ID": novo_id, "Nome do Serviço": s_nome, "Preço (R$)": s_preco}])
                        servicos_df = pd.concat([servicos_df, novo_s], ignore_index=True)
                        servicos_df.to_csv(ARQUIVO_SERVICOS, index=False, encoding='utf-8')
                        st.success("✨ Serviço criado!")
                        time.sleep(1.2)
                        st.rerun()
            with st.container(border=True):
                st.subheader("Editar ou Excluir Serviço Existente")
                servico_editar = st.selectbox("Escolha o Serviço:", servicos_df["Nome do Serviço"].tolist(), key="sb_edit_s")
                novo_preco_s = st.number_input("Modificar Valor:", min_value=0.0, value=float(servicos_df[servicos_df["Nome do Serviço"] == servico_editar]["Preço (R$)"].values[0]), key="num_edit_s")
                c_btn_s1, c_btn_s2 = st.columns(2)
                with c_btn_s1:
                    if st.button("Atualizar Preço", type="primary", use_container_width=True):
                        servicos_df.loc[servicos_df["Nome do Serviço"] == servico_editar, "Preço (R$)"] = novo_preco_s
                        servicos_df.to_csv(ARQUIVO_SERVICOS, index=False, encoding='utf-8')
                        st.success("🎉 Preço updated!")
                        time.sleep(1.2)
                        st.rerun()
                with c_btn_s2:
                    if st.session_state["perfil"] == "admin":
                        if st.button("❌ Excluir Serviço", use_container_width=True):
                            servicos_df = servicos_df[servicos_df["Nome do Serviço"] != servico_editar]
                            servicos_df.to_csv(ARQUIVO_SERVICOS, index=False, encoding='utf-8')
                            st.success("🗑️ Serviço excluído!")
                            time.sleep(1.2)
                            st.rerun()
                    else: st.error("🚫 Bloqueado")
        with col_s_2: st.dataframe(servicos_df, use_container_width=True, hide_index=True)

    with aba_prod:
        col_p_1, col_p_2 = st.columns(2, gap="large")
        with col_p_1:
            with st.container(border=True):
                st.subheader("Cadastrar Novo Produto")
                col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
                with col_p1: p_nome = st.text_input("Nome do Produto:")
                with col_p2: p_venda = st.number_input("Preço Venda:")
                with col_p3: p_custo = st.number_input("Preço Custo:")
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
            with st.container(border=True):
                st.subheader("Editar ou Excluir Produto Existente")
                prod_editar = st.selectbox("Selecione o Produto:", produtos_df["Nome do Produto"].tolist(), key="sb_edit_p")
                col_ed1, col_ed2, col_ed3, col_ed4 = st.columns(4)
                item_linha = produtos_df[produtos_df["Nome do Produto"] == prod_editar]
                with col_ed1: ed_venda = st.number_input("Preço Venda:", value=float(item_linha["Preço de Venda"].values[0]), key="num_p_v")
                with col_ed2: ed_custo = st.number_input("Preço Custo:", value=float(item_linha["Preço de Custo"].values[0]), key="num_p_c")
                with col_ed3: ed_estoque = st.number_input("Estoque Inicial:", value=int(item_linha["Estoque Inicial"].values[0]), key="num_p_e")
                with col_ed4: ed_comis = st.number_input("Comissão Fixa R$:", value=float(item_linha["Comissão Barbeiro (R$)"].values[0]), key="num_p_cm")
                c_btn_p1, c_btn_p2 = st.columns(2)
                with c_btn_p1:
                    if st.button("Salvar Modificações", type="primary", use_container_width=True):
                        produtos_df.loc[produtos_df["Nome do Produto"] == prod_editar, ["Preço de Venda", "Preço de Custo", "Estoque Inicial", "Comissão Barbeiro (R$)"]] = [ed_venda, ed_custo, ed_estoque, ed_comis]
                        produtos_df.to_csv(ARQUIVO_PRODUTOS, index=False, encoding='utf-8')
                        st.success("🎉 Informações updated!")
                        time.sleep(1.2)
                        st.rerun()
                with c_btn_p2:
                    if st.session_state["perfil"] == "admin":
                        if st.button("❌ Excluir Produto", use_container_width=True):
                            produtos_df = produtos_df[produtos_df["Nome do Produto"] != prod_editar]
                            produtos_df.to_csv(ARQUIVO_PRODUTOS, index=False, encoding='utf-8')
                            st.success("🗑️ Produto excluído!")
                            time.sleep(1.2)
                            st.rerun()
                    else: st.error("🚫 Bloqueado")
        with col_p_2: st.dataframe(produtos_df, use_container_width=True, hide_index=True)

# ---------------- MÓDULO 9: GERENCIAR USUÁRIOS ----------------
elif menu == "👤 Gerenciar Usuários":
    if st.session_state["perfil"] == "admin":
        st.header("👤 Gerenciamento de Usuários e Níveis de Acesso")
        tab_usr1, tab_usr2 = st.tabs(["➕ Criar Novo Perfil", "✏️ Editar ou Resetar Perfil Existente"])
        with tab_usr1:
            col_u1, col_u2 = st.columns(2, gap="large")
            with col_u1:
                with st.container(border=True):
                    novo_usr = st.text_input("Nome do Usuário de Login (Sem espaços):", key="n_u_add").strip().lower()
                    nova_pwd = st.text_input("Definir Senha de Acesso:", type="password", key="n_p_add")
                    st.write("**Marque quais telas este usuário poderá ver:**")
                    p_comanda = st.checkbox("💸 Abrir Comanda (Vendas)", value=True, key="add_comanda")
                    p_clube = st.checkbox("💳 Clube de Assinaturas", key="add_clube")
                    p_gastos = st.checkbox("📉 Lançar Gasto/Despesa", key="add_gastos")
                    p_correcao = st.checkbox("✏️ Corrigir Lançamentos", key="add_correcao")
                    p_fechamento = st.checkbox("🔒 Fechamento de Dia", key="add_fechamento")
                    p_barbeiro = st.checkbox("👥 Cadastrar Barbeiro", key="add_barbeiro")
                    p_estoque = st.checkbox("📦 Estoque & Serviços", value=True, key="add_estoque")
                    p_catalogo = st.checkbox("⚙️ Gerenciar Catálogo", key="add_catalogo")
                    p_ger_usr = st.checkbox("👤 Gerenciar Usuários", key="add_ger_usr")
                    p_relatorios = st.checkbox("📊 Painel de Relatórios", key="add_relatorios")
                    p_emitir_r = st.checkbox("📄 Emitir Relatórios", key="add_emitir_r")
                    p_backup = st.checkbox("💾 Backup do Sistema", key="add_backup")
                    p_config = st.checkbox("⚙️ Configurações", key="add_config")
                    if st.button("💾 Gravar Novo Usuário", type="primary", use_container_width=True, key="btn_add_user"):
                        if novo_usr and nova_pwd:
                            if novo_usr not in usuarios_df["Usuario"].str.lower().tolist():
                                lista_p = []
                                if p_comanda: lista_p.append("💸 Abrir Comanda (Vendas)")
                                if p_clube: lista_p.append("💳 Clube de Assinaturas")
                                if p_gastos: lista_p.append("📉 Lançar Gasto/Despesa")
                                if p_correcao: lista_p.append("✏️ Corrigir Lançamentos")
                                if p_fechamento: lista_p.append("🔒 Fechamento de Dia")
                                if p_barbeiro: lista_p.append("👥 Cadastrar Barbeiro")
                                if p_estoque: lista_p.append("📦 Estoque & Serviços")
                                if p_catalogo: lista_p.append("⚙️ Gerenciar Catálogo")
                                if p_ger_usr: lista_p.append("👤 Gerenciar Usuários")
                                if p_relatorios: lista_p.append("📊 Painel de Relatórios")
                                if p_emitir_r: lista_p.append("📄 Emitir Relatórios")
                                if p_backup: lista_p.append("💾 Backup do Sistema")
                                if p_config: lista_p.append("⚙️ Configurações")
                                perm_formatada = "|".join(lista_p)
                                novo_u_df = pd.DataFrame([{"Usuario": novo_usr, "Senha": nova_pwd, "Permissoes": perm_formatada}])
                                usuarios_df = pd.concat([usuarios_df, novo_u_df], ignore_index=True)
                                usuarios_df.to_csv(ARQUIVO_USUARIOS, index=False, encoding='utf-8')
                                st.success("🎉 Criado com sucesso!")
                                time.sleep(1.2)
                                st.rerun()
                            else: st.error("Usuário já existe.")
            with col_u2: st.dataframe(usuarios_df[["Usuario", "Permissoes"]], use_container_width=True, hide_index=True)

        with tab_usr2:
            lista_usuarios_editaveis = [u for u in usuarios_df["Usuario"].tolist() if u.lower() != "admin"]
            if lista_usuarios_editaveis:
                usuario_selecionado = st.selectbox("Selecione qual usuário deseja editar:", lista_usuarios_editaveis, key="sb_edit_user_sel")
                linha_user = usuarios_df[usuarios_df["Usuario"] == usuario_selecionado].iloc[0]
                permissões_atuais = str(linha_user["Permissoes"]).split("|")
                col_ed_u1, col_ed_u2 = st.columns(2, gap="large")
                with col_ed_u1:
                    with st.container(border=True):
                        st.markdown(f"#### 🔒 Resetar Senha: **{usuario_selecionado.upper()}**")
                        nova_senha_user = st.text_input("Nova Senha:", value=str(linha_user["Senha"]), key="n_p_edit_val")
                        st.markdown("#### ⚙️ Telas de Acesso")
                        e_comanda = st.checkbox("💸 Abrir Comanda", value=("💸 Abrir Comanda (Vendas)" in permissões_atuais), key="edit_comanda")
                        e_clube = st.checkbox("💳 Clube de Assinaturas", value=("💳 Clube de Assinaturas" in permissões_atuais), key="edit_clube")
                        e_gastos = st.checkbox("📉 Lançar Gasto", value=("📉 Lançar Gasto/Despesa" in permissões_atuais), key="edit_gastos")
                        e_correcao = st.checkbox("✏️ Corrigir Lançamentos", value=("✏️ Corrigir Lançamentos" in permissões_atuais), key="edit_correcao")
                        e_fechamento = st.checkbox("🔒 Fechamento de Dia", value=("🔒 Fechamento de Dia" in permissões_atuais), key="edit_fechamento")
                        e_barbeiro = st.checkbox("👥 Cadastrar Barbeiro", value=("👥 Cadastrar Barbeiro" in permissões_atuais), key="edit_barbeiro")
                        e_estoque = st.checkbox("📦 Estoque & Serviços", value=("📦 Estoque & Serviços" in permissões_atuais), key="edit_estoque")
                        e_catalogo = st.checkbox("⚙️ Gerenciar Catálogo", value=("⚙️ Gerenciar Catálogo" in permissões_atuais), key="edit_catalogo")
                        e_ger_usr = st.checkbox("👤 Gerenciar Usuários", value=("👤 Gerenciar Usuários" in permissões_atuais), key="edit_ger_usr")
                        e_relatorios = st.checkbox("📊 Painel de Relatórios", value=("📊 Painel de Relatórios" in permissões_atuais), key="edit_relatorios")
                        e_emitir_r = st.checkbox("📄 Emitir Relatórios", value=("📄 Emitir Relatórios" in permissões_atuais), key="edit_emitir_r")
                        e_backup = st.checkbox("💾 Backup do Sistema", value=("💾 Backup do Sistema" in permissões_atuais), key="edit_backup")
                        e_config = st.checkbox("⚙️ Configurações", value=("⚙️ Configurações" in permissões_atuais), key="edit_config")
                        
                        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True, key="btn_save_edit_user"):
                            lista_novas_p = []
                            if e_comanda: lista_novas_p.append("💸 Abrir Comanda (Vendas)")
                            if e_clube: lista_novas_p.append("💳 Clube de Assinaturas")
                            if e_gastos: lista_novas_p.append("📉 Lançar Gasto/Despesa")
                            if e_correcao: lista_novas_p.append("✏️ Corrigir Lançamentos")
                            if e_fechamento: lista_novas_p.append("🔒 Fechamento de Dia")
                            if e_barbeiro: lista_novas_p.append("👥 Cadastrar Barbeiro")
                            if e_estoque: lista_novas_p.append("📦 Estoque & Serviços")
                            if e_catalogo: lista_novas_p.append("⚙️ Gerenciar Catálogo")
                            if e_ger_usr: lista_novas_p.append("👤 Gerenciar Usuários")
                            if e_relatorios: lista_novas_p.append("📊 Painel de Relatórios")
                            if e_emitir_r: lista_novas_p.append("📄 Emitir Relatórios")
                            if e_backup: lista_novas_p.append("💾 Backup do Sistema")
                            if e_config: lista_novas_p.append("⚙️ Configurações")
                            
                            usuarios_df.loc[usuarios_df["Usuario"] == usuario_selecionado, "Senha"] = nova_senha_user
                            usuarios_df.loc[usuarios_df["Usuario"] == usuario_selecionado, "Permissoes"] = "|".join(lista_novas_p)
                            usuarios_df.to_csv(ARQUIVO_USUARIOS, index=False, encoding='utf-8')
                            st.success("⚙️ Perfil updated!")
                            time.sleep(1.2)
                            st.rerun()
                with col_ed_u2:
                    with st.container(border=True):
                        st.subheader("🗑️ Remover Conta")
                        if st.button("Bloquear e Excluir Usuário", use_container_width=True, key="btn_del_user"):
                            usuarios_df = usuarios_df[usuarios_df["Usuario"] != usuario_selecionado]
                            usuarios_df.to_csv(ARQUIVO_USUARIOS, index=False, encoding='utf-8')
                            st.success(f"Removido!")
                            time.sleep(1.2)
                            st.rerun()
            else: st.info("Nenhum usuário cadastrado para alteração no momento.")
    else: st.error("🚨 ÁREA RESTRITA AO SUPER ADMINISTRADOR.")

# ---------------- MÓDULO 10: PAINEL DE RELATÓRIOS ----------------
elif menu == "📊 Painel de Relatórios":
    st.header("📊 Dashboard Financeiro - O Chefão")
    vendas_df["Valor Total"] = pd.to_numeric(vendas_df["Valor Total"], errors='coerce').fillna(0)
    vendas_df["Quantidade"] = pd.to_numeric(vendas_df["Quantidade"], errors='coerce').fillna(0)
    gastos_df["Valor (R$)"] = pd.to_numeric(gastos_df["Valor (R$)"], errors='coerce').fillna(0)
    consumo_interno_df["Valor Total"] = pd.to_numeric(consumo_interno_df["Valor Total"], errors='coerce').fillna(0)
    consumo_interno_df["Quantidade"] = pd.to_numeric(consumo_interno_df["Quantidade"], errors='coerce').fillna(0)
    vendas_df["Ano_Mes"] = vendas_df["Data"].str[:7]
    gastos_df["Ano_Mes"] = gastos_df["Data"].str[:7]
    meses_disponiveis = sorted(list(set(vendas_df["Ano_Mes"].dropna().tolist() + gastos_df["Ano_Mes"].dropna().tolist())), reverse=True)
    mes_atual_string = datetime.now().strftime("%Y-%m")
    if mes_atual_string not in meses_disponiveis: meses_disponiveis.insert(0, mes_atual_string)
    mes_selecionado = st.selectbox("📅 Selecione o Mês de Análise:", meses_disponiveis, index=0)
    vendas_filtradas = vendas_df[vendas_df["Ano_Mes"] == mes_selecionado]
    gastos_filtrados = gastos_df[gastos_df["Ano_Mes"] == mes_selecionado]
    faturamento_mes = vendas_filtradas["Valor Total"].sum()
    total_gastos_mes = gastos_filtrados["Valor (R$)"].sum()
    lucro_liquido_mes = faturamento_mes - total_gastos_mes
    
    c1, c2, c3 = st.columns(3)
    c1.metric(f"💰 FATURAMENTO ({mes_selecionado})", f"R$ {faturamento_mes:.2f}")
    c2.metric(f"📉 GASTOS ({mes_selecionado})", f"R$ {total_gastos_mes:.2f}")
    c3.metric(f"🔥 LUCRO LÍQUIDO ({mes_selecionado})", f"R$ {lucro_liquido_mes:.2f}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    tab_rel1, tab_rel2, tab_rel3 = st.tabs(["💸 Fechamento Semanal & Comissões", "🥤 Consumo Interno (Staff)", "📅 Visão Mensal Expandida"])
    with tab_rel1:
        if not barbeiros_df.empty:
            relatorio_comissao = []
            mapa_comissao_produto = produtos_df.set_index("Nome do Produto")["Comissão Barbeiro (R$)"].to_dict()
            mapa_desconto_consumo = consumo_interno_df.groupby("Responsavel")["Valor Total"].sum().to_dict()
            for _, b in barbeiros_df.iterrows():
                nome_b = b["Nome"]
                porcentagem_servico = b["Comissão (%)"]
                vendas_do_barbeiro = vendas_df[vendas_df["Barbeiro"] == nome_b]
                servicos_b = vendas_do_barbeiro[vendas_do_barbeiro["Tipo"] == "Serviço"]
                valor_comissao_servico = servicos_b["Valor Total"].sum() * (porcentagem_servico / 100.0)
                produtos_b = vendas_do_barbeiro[vendas_do_barbeiro["Tipo"] == "Produto"]
                valor_comissao_produto = sum([float(mapa_comissao_produto.get(v["Item"], 0.0)) * float(v["Quantidade"]) for _, v in produtos_b.iterrows()])
                total_ganho_bruto = valor_comissao_servico + valor_comissao_produto
                valor_divida_consumo = float(mapa_desconto_consumo.get(nome_b, 0.0))
                relatorio_comissao.append({
                    "Profissional": nome_b, "Comissão Serv.": f"R$ {valor_comissao_servico:.2f}", "Comissão Prod.": f"R$ {valor_comissao_produto:.2f}",
                    "Ganho Bruto (A)": f"R$ {total_ganho_bruto:.2f}", "Dívida Consumo (B)": f"R$ {valor_divida_consumo:.2f}", "PAGAMENTO LÍQUIDO": f"R$ {total_ganho_bruto - valor_divida_consumo:.2f}"
                })
            st.dataframe(pd.DataFrame(relatorio_comissao), use_container_width=True, hide_index=True)
    with tab_rel2:
        lista_staff = barbeiros_df["Nome"].tolist() if not barbeiros_df.empty else []
        if "admin" not in lista_staff: lista_staff.append("admin")
        quem_consumiu = st.selectbox("Quem consumiu?", lista_staff)
        produto_retirado = st.selectbox("Produto Retirado:", produtos_df["Nome do Produto"].tolist())
        qtd_retirada = st.number_input("Quantidade:", min_value=1, value=1)
        if st.button("💾 Gravar Consumo", type="primary"):
            preco_v = produtos_df[produtos_df["Nome do Produto"] == produto_retirado]["Preço de Venda"].values[0]
            novo_c = pd.DataFrame([{"Data": datetime.now().strftime("%Y-%m-%d"), "Responsavel": quem_consumiu, "Item": produto_retirado, "Quantidade": qtd_retirada, "Valor Total": float(preco_v) * qtd_retirada}])
            consumo_interno_df = pd.concat([consumo_interno_df, novo_c], ignore_index=True)
            consumo_interno_df.to_csv(ARQUIVO_CONSUMO_INTERNO, index=False, encoding='utf-8')
            st.success("Salvo!")
            st.rerun()
        if st.session_state["perfil"] == "admin":
            if st.button("⚠️ Limpar Extrato da Semana (Apenas Admin)"):
                pd.DataFrame(columns=["Data", "Responsavel", "Item", "Quantidade", "Valor Total"]).to_csv(ARQUIVO_CONSUMO_INTERNO, index=False, encoding='utf-8')
                st.rerun()
    with tab_rel3:
        if not vendas_filtradas.empty: st.line_chart(vendas_filtradas.groupby("Data")["Valor Total"].sum())

# ---------------- MÓDULO 11: EMISSÃO DE RELATÓRIOS OFICIAIS EM PDF ----------------
elif menu == "📄 Emitir Relatórios":
    st.header("📄 Emissão de Relatórios Oficiais (PDF)")
    st.write("Filtre o período comercial desejado para gerar e exportar o documento consolidado do caixa.")
    
    with st.container(border=True):
        tipo_filtro = st.radio("Selecione o Intervalo de Tempo:", ["Por Dia Específico", "Por Mês Inteiro", "Período Customizado (Trimestral/Semestral)"])
        
        # Lógica de definição de datas com base no seletor
        if tipo_filtro == "Por Dia Específico":
            dia_sel = st.date_input("Escolha o Dia:", datetime.now())
            data_inicio = dia_sel.strftime("%Y-%m-%d")
            data_fim = dia_sel.strftime("%Y-%m-%d")
        elif tipo_filtro == "Por Mês Inteiro":
            mes_sel = st.text_input("Digite o Ano-Mês (Formato YYYY-MM):", value=datetime.now().strftime("%Y-%m"))
            data_inicio = f"{mes_sel}-01"
            data_fim = f"{mes_sel}-31"
        else:
            col_d1, col_d2 = st.columns(2)
            data_inicio = col_d1.date_input("Data de Início:", datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
            data_fim = col_d2.date_input("Data de Fim:", datetime.now()).strftime("%Y-%m-%d")
            
        st.markdown("---")
        
        if st.button("🧱 Processar e Compilar Relatório PDF", type="primary", use_container_width=True):
            # Filtragem Cirúrgica dos DataFrames
            vendas_df["Data"] = vendas_df["Data"].astype(str)
            v_filtradas = vendas_df[(vendas_df["Data"] >= data_inicio) & (vendas_df["Data"] <= data_fim)]
            
            gastos_df["Data"] = gastos_df["Data"].astype(str)
            g_filtrados = gastos_df[(gastos_df["Data"] >= data_inicio) & (gastos_df["Data"] <= data_fim)]
            
            fechamentos_df["Data"] = fechamentos_df["Data"].astype(str)
            f_filtrados = fechamentos_df[(fechamentos_df["Data"] >= data_inicio) & (fechamentos_df["Data"] <= data_fim)]

            # Cálculos consolidados para exibição estruturada
            faturamento_tot = pd.to_numeric(v_filtradas["Valor Total"], errors='coerce').sum()
            gastos_tot = pd.to_numeric(g_filtrados["Valor (R$)"], errors='coerce').sum()
            saldo_liq = faturamento_tot - gastos_tot
            
            # Montagem do PDF utilizando FPDF2
            pdf = PDFRelatorio()
            pdf.add_page()
            
            # Bloco 1: Informações Gerais do Período
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"Periodo Auditado: {data_inicio} ate {data_fim}", ln=1)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 6, f"Emitido por: {st.session_state['perfil'].upper()} em {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=1)
            pdf.ln()
            
            # Bloco 2: Resumo Financeiro
            pdf.set_font("Arial", "B", 11)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 7, "1. RESUMO FINANCEIRO GERAL", ln=1, fill=True)
            pdf.set_font("Arial", "", 10)
            pdf.cell(95, 6, f" Faturamento Bruto Balcao: R$ {faturamento_tot:.2f}", border=1)
            pdf.cell(95, 6, f" Total de Saidas (Gastos): R$ {gastos_tot:.2f}", border=1, ln=1)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(190, 6, f" Saldo Liquido do Periodo: R$ {saldo_liq:.2f}", border=1, ln=1)
            pdf.ln()
            
            # Bloco 3: Movimentação de Atendimentos e Categorias
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, "2. DETALHAMENTO POR CATEGORIA DE ATENDIMENTO", ln=1, fill=True)
            pdf.set_font("Arial", "", 10)
            servicos_tot = v_filtradas[v_filtradas["Tipo"] == "Serviço"]["Valor Total"].sum()
            produtos_tot = v_filtradas[v_filtradas["Tipo"] == "Produto"]["Valor Total"].sum()
            pdf.cell(95, 6, f" Faturamento com Servicos (Barbearia): R$ {servicos_tot:.2f}", border=1)
            pdf.cell(95, 6, f" Faturamento com Produtos (Conveniencia): R$ {produtos_tot:.2f}", border=1, ln=1)
            pdf.ln()
            
            # Bloco 4: Divisão por Meios de Recebimento
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, "3. RECEBIMENTOS POR MEIO DE PAGAMENTO", ln=1, fill=True)
            pdf.set_font("Arial", "", 10)
            for meio in ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"]:
                val_meio = v_filtradas[v_filtradas["Forma de Pagamento"] == meio]["Valor Total"].sum()
                pdf.cell(47.5, 6, f" {meio}: R$ {val_meio:.2f}", border=1)
            pdf.ln()
            pdf.ln()
            
            # Bloco 5: Histórico de Quebras de Caixa
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, "4. AUDITORIA DE FECHAMENTOS DE CAIXA DIARIOS", ln=1, fill=True)
            pdf.set_font("Arial", "B", 9)
            pdf.cell(40, 6, "Data", border=1, align="C")
            pdf.cell(40, 6, "Usuario", border=1, align="C")
            pdf.cell(50, 6, "Total Contado", border=1, align="C")
            pdf.cell(60, 6, "Diferenca / Status", border=1, align="C", ln=1)
            pdf.set_font("Arial", "", 9)
            if not f_filtrados.empty:
                for _, fech in f_filtrados.iterrows():
                    pdf.cell(40, 6, str(fech["Data"]), border=1, align="C")
                    pdf.cell(40, 6, str(fech["Usuario"]).upper(), border=1, align="C")
                    pdf.cell(50, 6, f"R$ {fech['Total Real']:.2f}", border=1, align="C")
                    pdf.cell(60, 6, str(fech["Status"]), border=1, align="C", ln=1)
            else:
                pdf.cell(190, 6, "Nenhum fechamento auditado gravado no intervalo selecionado.", border=1, ln=1, align="C")
                
            # Exportação segura do buffer binário
            pdf_output = pdf.output(dest='S')
            st.download_button(
                label="📥 Baixar Relatório Gerado (PDF)",
                data=bytes(pdf_output),
                file_name=f"relatorio_ochefao_{data_inicio}_a_{data_fim}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            st.success("✨ Relatório generated! Clique no botão acima para salvar o PDF.")

# ---------------- MÓDULO 12: TELA DE BACKUP UNIFICADO ----------------
elif menu == "💾 Backup do Sistema":
    if st.session_state["perfil"] == "admin":
        st.header("💾 Sistema Unificado de Backup Completo (.ZIP)")
        aba_exp_zip, aba_imp_zip = st.tabs(["📥 1. Criar e Baixar Backup Total", "📤 2. Restaurar Sistema Completo"])
        with aba_exp_zip:
            buffer_zip = io.BytesIO()
            with zipfile.ZipFile(buffer_zip, "w") as arquivo_zip:
                for nome_csv, caminho_real in TODOS_ARQUIVOS_BACKUP.items():
                    if os.path.exists(caminho_real): arquivo_zip.write(caminho_real, arcname=nome_csv)
            buffer_zip.seek(0)
            st.download_button(label="📥 Baixar Backup Completo (ZIP)", data=buffer_zip, file_name=f"backup_total_ochefao_{datetime.now().strftime('%Y%m%d')}.zip", mime="application/zip", use_container_width=True)
        with aba_imp_zip:
            st.subheader("Suba o arquivo .ZIP para restaurar tudo:")
            arquivo_zip_subido = st.file_uploader("Escolha o arquivo unificado (.zip):", type=["zip"])
            if arquivo_zip_subido is not None:
                if st.button("🚀 Restaurar Todo o Sistema", type="primary", use_container_width=True):
                    try:
                        with zipfile.ZipFile(arquivo_zip_subido, "r") as z:
                            for nome_csv, caminho_real in TODOS_ARQUIVOS_BACKUP.items():
                                if nome_csv in z.namelist():
                                    dados_extraidos = z.read(nome_csv)
                                    with open(caminho_real, "wb") as f: f.write(dados_extraidos)
                        st.success("🔥 SUCESSO! Sistema restaurado!")
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e: st.error(f"Erro: {e}")
    else: st.error("🚨 ÁREA RESTRITA AO SUPER ADMINISTRADOR.")

# ---------------- MÓDULO 13: CONFIGURAÇÕES ----------------
elif menu == "⚙️ Configurações":
    if st.session_state["perfil"] == "admin":
        st.header("Configurações Globais")
        with st.container(border=True):
            if st.button("🚨 Zerar Clientes de Assinatura", type="primary", use_container_width=True):
                pd.DataFrame(columns=["Cliente", "Plano", "Data Inicio", "Data Vencimento", "Valor Mensal"]).to_csv(ARQUIVO_ASSINATURAS, index=False, encoding='utf-8')
                pd.DataFrame(columns=["Data", "Cliente", "Serviço Usado", "Barbeiro Atendeu"]).to_csv(ARQUIVO_PRESENCAS, index=False, encoding='utf-8')
                st.success("Clube resetado!")
                st.rerun()
        with st.container(border=True):
            if st.button("🚨 Limpar Todas as Vendas e Zerar Caixa", use_container_width=True):
                pd.DataFrame(columns=["Data", "Item", "Tipo", "Quantidade", "Valor Total", "Forma de Pagamento", "Barbeiro", "Cliente"]).to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
                st.success("Caixa redefinido!")
                st.rerun()
    else: st.error("🚨 ÁREA RESTRITA AO SUPER ADMINISTRADOR.")
