import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import zipfile
import io
import base64
from fpdf import FPDF

# [CONFIGURAÇÕES E INICIALIZAÇÃO SE MANTÊM IGUAIS, APENAS ATUALIZE A TELA DE COMANDA]

# ... (MANTENHA TODO O INÍCIO DO CÓDIGO ATÉ O MENU "💸 Abrir Comanda (Vendas)") ...

# ---------------- MÓDULO 1: COMANDA ELETRÔNICA (ATUALIZADO PARA PAGAMENTO MISTO) ----------------
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
                
                # --- PAGAMENTO MISTO ---
                st.subheader("💳 Pagamento Misto")
                v_dinheiro = st.number_input("Valor em Dinheiro (R$):", min_value=0.0, value=0.0, step=0.50)
                v_pix_cartao = st.number_input("Valor em Pix/Cartão (R$):", min_value=0.0, value=0.0, step=0.50)
                tipo_pix_cartao = st.selectbox("Tipo de Pix/Cartão:", ["Pix", "Cartão de Crédito", "Cartão de Débito"])
                
                soma_pagamentos = v_dinheiro + v_pix_cartao
                saldo_restante = valor_total_comanda - soma_pagamentos
                
                if saldo_restante > 0: st.warning(f"⚠️ Saldo restante para pagar: R$ {saldo_restante:.2f}")
                elif saldo_restante < 0: st.error(f"❌ Valor pago excede o total em: R$ {abs(saldo_restante):.2f}")
                else: st.success("✅ Pagamento conferido!")
                
                lista_barbeiros_sistema = barbeiros_df["Nome"].tolist() if not barbeiros_df.empty else ["G."]
                barbeiro_venda = st.selectbox("Barbeiro Executor:", lista_barbeiros_sistema)
                cliente = st.text_input("Identificação do Cliente:", value="Avulso")
                
                if st.button("🚀 Finalizar Conta", type="primary", use_container_width=True, disabled=(saldo_restante != 0)):
                    data_final = datetime.now().strftime("%Y-%m-%d")
                    registros = []
                    # Grava linha para Dinheiro
                    if v_dinheiro > 0:
                        registros.append({"Data": data_final, "Item": "PAGAMENTO DINHEIRO", "Tipo": "Financeiro", "Quantidade": 1, "Valor Total": v_dinheiro, "Forma de Pagamento": "Dinheiro", "Barbeiro": barbeiro_venda, "Cliente": cliente})
                    # Grava linha para Pix/Cartão
                    if v_pix_cartao > 0:
                        registros.append({"Data": data_final, "Item": f"PAGAMENTO {tipo_pix_cartao.upper()}", "Tipo": "Financeiro", "Quantidade": 1, "Valor Total": v_pix_cartao, "Forma de Pagamento": tipo_pix_cartao, "Barbeiro": barbeiro_venda, "Cliente": cliente})
                    
                    # Grava os itens da comanda
                    for item_c in st.session_state["carrinho_comanda"]:
                        item_c["Data"] = data_final
                        item_c["Forma de Pagamento"] = "Consumo"
                        item_c["Barbeiro"] = barbeiro_venda
                        item_c["Cliente"] = cliente
                        registros.append(item_c)
                        
                    vendas_df = pd.concat([vendas_df, pd.DataFrame(registros)], ignore_index=True)
                    vendas_df.to_csv(ARQUIVO_VENDAS, index=False, encoding='utf-8')
                    st.session_state["carrinho_comanda"] = []
                    st.success("✅ Venda e Pagamento Misto registrados!")
                    time.sleep(1.2)
                    st.rerun()

# ... (MANTENHA O RESTANTE DO CÓDIGO ABAIXO IGUAL) ...
