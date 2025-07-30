# app.py
# Para rodar este app:
# 1. Salve este código como `app.py`.
# 2. Certifique-se de que seu `requirements.txt` está atualizado.
# 3. No terminal, execute: streamlit run app.py

import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from streamlit_calendar import calendar
from streamlit_option_menu import option_menu

# --- Configuração da Página ---
st.set_page_config(
    page_title="Gestão DeMolay - Mariano Fedele",
    page_icon="https://i.ibb.co/nsF1xTF0/image.jpg",
    layout="wide"
)

# --- DADOS E AUTENTICAÇÃO ---
SENHA_ADMIN = "cascao"
SENHA_VISITANTE = "zegotinha"
VALOR_MENSALIDADE = 25.00

def get_proximo_id(df, id_column):
    """Gera um novo ID único para um DataFrame."""
    if df.empty or not df[id_column].any():
        return 1
    return int(df[id_column].max() + 1)

def initialize_data():
    """Inicializa ou reseta os dados no estado da sessão."""
    if 'membros_df' not in st.session_state:
        st.session_state.membros_df = pd.DataFrame({
            'id_membro': [1, 2, 3, 4], 'cid': ['12345', '54321', '67890', '09876'],
            'nome': ['João da Silva', 'Carlos Pereira', 'Pedro Almeida', 'Lucas Souza'],
            'telefone': ['(51) 99999-1111', '(51) 98888-2222', '(51) 97777-3333', '(51) 96666-4444'],
            'status': ['Ativo', 'Ativo', 'Sênior', 'Ativo'],
            'email': ['joao@email.com', 'carlos@email.com', 'pedro@email.com', 'lucas@email.com']
        })
    if 'eventos_df' not in st.session_state:
        st.session_state.eventos_df = pd.DataFrame({
            'id_evento': [101, 102, 103], 'data': pd.to_datetime(['2025-07-28', '2025-08-09', '2025-08-16']),
            'evento': ['Reunião Ordinária', 'Filantropia - Asilo', 'Cerimônia Magna de Iniciação'],
            'descricao': ['Discussão de projetos.', 'Visita e doação.', 'Iniciação de novos membros.'],
            'cor': ['#FF6347', '#4682B4', '#32CD32']
        })
    if 'tesouraria_df' not in st.session_state:
        st.session_state.tesouraria_df = pd.DataFrame({
            'id_transacao': [1, 2, 3], 'data': pd.to_datetime(['2025-07-01', '2025-07-05', '2025-07-15']),
            'descricao': ['Taxa mensal - João', 'Compra de materiais', 'Taxa mensal - Carlos'],
            'tipo': ['Entrada', 'Saída', 'Entrada'], 'valor': [20.00, -15.50, 20.00]
        })
    if 'mensalidades_df' not in st.session_state:
        st.session_state.mensalidades_df = pd.DataFrame({
            'id_membro': [1, 2, 4], 'status_pagamento': ['Adimplente', 'Inadimplente', 'Adimplente']
        })
    if 'presenca_df' not in st.session_state:
        st.session_state.presenca_df = pd.DataFrame({
            'id_evento': pd.Series(dtype='int'), 'id_membro': pd.Series(dtype='int'),
            'presente': pd.Series(dtype='bool')
        })
    if 'projecao_extras' not in st.session_state:
        st.session_state.projecao_extras = {}
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()

def update_timestamp():
    """Atualiza o timestamp da última modificação."""
    st.session_state.last_update = datetime.now()

# --- TELA DE LOGIN ---
def login_screen():
    st.title("Sistema de Gestão do Capítulo Mariano Fedele")
    st.subheader("Por favor, insira a senha de acesso para continuar")
    with st.form("login_form"):
        password = st.text_input("Senha de Acesso", type="password")
        submitted = st.form_submit_button("Entrar")
        if submitted:
            if password == SENHA_ADMIN:
                st.session_state.authenticated = True
                st.session_state.role = "Admin"
                st.rerun()
            elif password == SENHA_VISITANTE:
                st.session_state.authenticated = True
                st.session_state.role = "Visitante"
                st.rerun()
            else:
                st.error("Senha inválida")

# --- LÓGICA PRINCIPAL DO APP ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_screen()
else:
    initialize_data()
    is_admin = st.session_state.role == "Admin"

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://i.ibb.co/nsF1xTF0/image.jpg", width=150)
    with col2:
        st.title("Gestão do Capítulo Mariano Fedele")
        st.markdown(f"Bem-vindo! (Perfil: **{st.session_state.role}**)")
    
    st.markdown("<hr>", unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["Visão Geral", "Membros", "Calendário", "Tesouraria", "Projetos", "Presença"],
        icons=['house', 'people', 'calendar-check', 'cash-coin', 'kanban', 'person-check'],
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#262730"},
            "icon": {"color": "white", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "--hover-color": "#3a3a4a"},
            "nav-link-selected": {"background-color": "#02ab21"},
        }
    )

    if selected == "Tesouraria":
        st.header("Gestão da Tesouraria")
        
        tab_options = ["Extrato", "Controle de Mensalidades", "Projeção Financeira", "Adicionar Lançamento"] if is_admin else ["Extrato", "Controle de Mensalidades"]
        tabs = st.tabs(tab_options)
        
        with tabs[0]: # Extrato
            saldo_total = st.session_state.tesouraria_df['valor'].sum()
            st.metric("Saldo Atual", f"R$ {saldo_total:,.2f}")
            st.dataframe(st.session_state.tesouraria_df.sort_values('data', ascending=False), use_container_width=True)

        with tabs[1]: # Mensalidades
            membros_ativos = st.session_state.membros_df[st.session_state.membros_df['status'] == 'Ativo']
            status_mensalidades = pd.merge(membros_ativos[['id_membro', 'nome']], st.session_state.mensalidades_df, on='id_membro', how='left').fillna({'status_pagamento': 'Inadimplente'})
            
            st.subheader("Status das Mensalidades")
            st.dataframe(status_mensalidades[['nome', 'status_pagamento']], use_container_width=True)

            if is_admin:
                with st.expander("Alterar Status de Pagamento"):
                    membro_select = st.selectbox("Selecione o Membro", options=status_mensalidades['nome'], key="sel_membro_mensal")
                    novo_status = st.radio("Novo Status", ['Adimplente', 'Inadimplente'], key="rad_status_mensal")
                    if st.button("Salvar Status"):
                        id_membro_alt = status_mensalidades.query(f"nome == '{membro_select}'")['id_membro'].iloc[0]
                        st.session_state.mensalidades_df = st.session_state.mensalidades_df.query(f"id_membro != {id_membro_alt}")
                        novo_status_df = pd.DataFrame([{'id_membro': id_membro_alt, 'status_pagamento': novo_status}])
                        st.session_state.mensalidades_df = pd.concat([st.session_state.mensalidades_df, novo_status_df], ignore_index=True)
                        update_timestamp()
                        st.success(f"Status de {membro_select} atualizado para {novo_status}!")
                        st.rerun()

        if is_admin:
            with tabs[2]: # Projeção Financeira
                st.subheader("Projeção de Fluxo de Caixa")
                
                # Setup
                today = datetime.today()
                meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
                projecao_data = []
                saldo_atual = st.session_state.tesouraria_df['valor'].sum()
                receita_mensalidades = len(st.session_state.membros_df[st.session_state.membros_df['status'] == 'Ativo']) * VALOR_MENSALIDADE

                # Inputs para valores extras
                st.write("Adicione entradas ou saídas extras para simular cenários:")
                cols = st.columns(4)
                
                saldo_projetado = saldo_atual
                
                for i in range(today.month, 13):
                    mes_ano_key = f"{i}-{today.year}"
                    mes_nome = meses_nomes[i-1]
                    
                    # Inicializa valores no session_state se não existirem
                    if mes_ano_key not in st.session_state.projecao_extras:
                        st.session_state.projecao_extras[mes_ano_key] = {'entradas': 0.0, 'saidas': 0.0}

                    with cols[(i-today.month) % 4]:
                        with st.container(border=True):
                            st.write(f"**{mes_nome}**")
                            st.session_state.projecao_extras[mes_ano_key]['entradas'] = st.number_input("Entradas Extras (+)", key=f"in_{mes_ano_key}", min_value=0.0, format="%.2f")
                            st.session_state.projecao_extras[mes_ano_key]['saidas'] = st.number_input("Saídas Extras (-)", key=f"out_{mes_ano_key}", min_value=0.0, format="%.2f")

                st.divider()
                st.subheader("Resultado da Projeção")

                # Geração da tabela de projeção
                for i in range(today.month, 13):
                    mes_ano_key = f"{i}-{today.year}"
                    mes_nome = meses_nomes[i-1]
                    
                    entradas_extras = st.session_state.projecao_extras[mes_ano_key]['entradas']
                    saidas_extras = st.session_state.projecao_extras[mes_ano_key]['saidas']
                    
                    saldo_final_mes = saldo_projetado + receita_mensalidades + entradas_extras - saidas_extras
                    
                    projecao_data.append({
                        "Mês": mes_nome,
                        "Saldo Inicial": f"R$ {saldo_projetado:,.2f}",
                        "Receita (Mensalidades)": f"R$ {receita_mensalidades:,.2f}",
                        "Entradas Extras": f"R$ {entradas_extras:,.2f}",
                        "Saídas Extras": f"R$ {saidas_extras:,.2f}",
                        "Saldo Final Projetado": f"R$ {saldo_final_mes:,.2f}"
                    })
                    
                    saldo_projetado = saldo_final_mes

                projecao_df = pd.DataFrame(projecao_data)
                st.dataframe(projecao_df, use_container_width=True)


            with tabs[3]: # Adicionar Lançamento
                with st.form("add_transacao", clear_on_submit=True):
                    # ... (código do formulário)
                    pass
    
    # ... (outras páginas como Visão Geral, Membros, Calendário, etc.)

    # --- RODAPÉ ---
    st.markdown("<hr>", unsafe_allow_html=True)
    last_update_str = st.session_state.last_update.strftime("%d/%m/%Y às %H:%M:%S")
    st.markdown(f"<p style='text-align: center; color: grey;'>Última atualização em: {last_update_str}</p>", unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.rerun()
