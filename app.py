# app.py
# Para rodar este app:
# 1. Salve este código como `app.py`.
# 2. Certifique-se de que seu `requirements.txt` está atualizado.
# 3. No terminal, execute: streamlit run app.py

import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar
from streamlit_option_menu import option_menu

# --- Configuração da Página ---
st.set_page_config(
    page_title="Gestão DeMolay - Mariano Fedele",
    page_icon="https://i.ibb.co/nsF1xTF0/image.jpg",
    layout="wide"
)

# --- DADOS E AUTENTICAÇÃO ---
ADMIN_USERS = {
    "admin": "demolay123",
    "mestreconselheiro": "demolay123",
    "escrivao": "demolay123"
}
VALOR_MENSALIDADE = 25.00 # Valor base para simulação

def get_proximo_id(df, id_column):
    """Gera um novo ID único para um DataFrame."""
    if df.empty or not df[id_column].any():
        return 1
    return int(df[id_column].max() + 1)

def initialize_data():
    """Inicializa ou reseta os dados no estado da sessão."""
    if 'membros_df' not in st.session_state:
        st.session_state.membros_df = pd.DataFrame({
            'id_membro': [1, 2, 3, 4],
            'cid': ['12345', '54321', '67890', '09876'],
            'nome': ['João da Silva', 'Carlos Pereira', 'Pedro Almeida', 'Lucas Souza'],
            'telefone': ['(51) 99999-1111', '(51) 98888-2222', '(51) 97777-3333', '(51) 96666-4444'],
            'status': ['Ativo', 'Ativo', 'Sênior', 'Ativo'],
            'email': ['joao@email.com', 'carlos@email.com', 'pedro@email.com', 'lucas@email.com']
        })
    if 'eventos_df' not in st.session_state:
        st.session_state.eventos_df = pd.DataFrame({
            'id_evento': [101, 102, 103],
            'data': pd.to_datetime(['2025-07-28', '2025-08-09', '2025-08-16']),
            'evento': ['Reunião Ordinária', 'Filantropia - Asilo', 'Cerimônia Magna de Iniciação'],
            'descricao': ['Discussão de projetos.', 'Visita e doação.', 'Iniciação de novos membros.'],
            'cor': ['#FF6347', '#4682B4', '#32CD32']
        })
    if 'tesouraria_df' not in st.session_state:
        st.session_state.tesouraria_df = pd.DataFrame({
            'id_transacao': [1, 2, 3],
            'data': pd.to_datetime(['2025-07-01', '2025-07-05', '2025-07-15']),
            'descricao': ['Taxa mensal - João', 'Compra de materiais', 'Taxa mensal - Carlos'],
            'tipo': ['Entrada', 'Saída'],
            'valor': [20.00, -15.50]
        })
    if 'mensalidades_df' not in st.session_state:
        st.session_state.mensalidades_df = pd.DataFrame({
            'id_membro': [1, 2, 4], # Apenas membros ativos
            'status_pagamento': ['Adimplente', 'Inadimplente', 'Adimplente']
        })
    if 'presenca_df' not in st.session_state:
        st.session_state.presenca_df = pd.DataFrame({
            'id_evento': pd.Series(dtype='int'),
            'id_membro': pd.Series(dtype='int'),
            'presente': pd.Series(dtype='bool')
        })
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()

def update_timestamp():
    """Atualiza o timestamp da última modificação."""
    st.session_state.last_update = datetime.now()

# --- TELA DE LOGIN ---
def login_screen():
    st.title("Sistema de Gestão do Capítulo Mariano Fedele")
    st.subheader("Por favor, faça o login para continuar")
    with st.form("login_form"):
        username = st.text_input("Usuário").lower()
        password = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")
        if submitted:
            if username in ADMIN_USERS and password == ADMIN_USERS[username]:
                st.session_state.authenticated = True
                st.session_state.role = "admin"
                st.session_state.username = username
                st.rerun()
            elif username:
                st.session_state.authenticated = True
                st.session_state.role = "visitante"
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

# --- LÓGICA PRINCIPAL DO APP ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_screen()
else:
    initialize_data()
    is_admin = st.session_state.role == "admin"

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://i.ibb.co/nsF1xTF0/image.jpg", width=150)
    with col2:
        st.title("Gestão do Capítulo Mariano Fedele")
        st.markdown(f"Bem-vindo, **{st.session_state.username}**! (Perfil: *{st.session_state.role}*)")
    
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

    if selected == "Visão Geral":
        st.header("Visão Geral do Capítulo")
        # ... (código da página)

    elif selected == "Membros":
        st.header("Gestão de Membros")
        # ... (código da página)

    elif selected == "Calendário":
        st.header("Calendário de Eventos")
        calendar_events = []
        for _, row in st.session_state.eventos_df.iterrows():
            calendar_events.append({"title": row["evento"], "start": row["data"].strftime("%Y-%m-%d"), "id": row["id_evento"], "color": row.get("cor", "#4682B4")})
        
        clicked_event = calendar(events=calendar_events, options={"locale": "pt-br"}, key=f"cal_{len(calendar_events)}")

        if is_admin and clicked_event and 'id' in clicked_event:
            event_id = int(clicked_event['id'])
            evento_data = st.session_state.eventos_df.query(f"id_evento == {event_id}").iloc[0]
            
            with st.expander("Editar ou Excluir Evento Selecionado", expanded=True):
                with st.form(f"edit_event_{event_id}"):
                    st.write(f"**Editando:** {evento_data['evento']}")
                    evento_edit = st.text_input("Nome do Evento", value=evento_data['evento'])
                    data_edit = st.date_input("Data", value=evento_data['data'])
                    cor_edit = st.color_picker("Cor do Evento", value=evento_data['cor'])
                    
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("Salvar Alterações"):
                        idx = st.session_state.eventos_df.index[st.session_state.eventos_df['id_evento'] == event_id].tolist()[0]
                        st.session_state.eventos_df.loc[idx, ['evento', 'data', 'cor']] = [evento_edit, pd.to_datetime(data_edit), cor_edit]
                        update_timestamp()
                        st.success("Evento atualizado!")
                        st.rerun()
                    if col2.form_submit_button("Excluir Evento", type="primary"):
                        st.session_state.eventos_df = st.session_state.eventos_df.query(f"id_evento != {event_id}").reset_index(drop=True)
                        update_timestamp()
                        st.warning("Evento excluído.")
                        st.rerun()

        if is_admin:
            with st.expander("Adicionar Novo Evento"):
                # ... (código do formulário de adicionar)
                pass

    elif selected == "Tesouraria":
        st.header("Gestão da Tesouraria")
        
        tab_options = ["Extrato", "Controle de Mensalidades", "Simulação de Receitas", "Adicionar Lançamento"] if is_admin else ["Extrato", "Controle de Mensalidades"]
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
                        
                        # Remove registro antigo se existir
                        st.session_state.mensalidades_df = st.session_state.mensalidades_df.query(f"id_membro != {id_membro_alt}")
                        # Adiciona novo registro
                        novo_status_df = pd.DataFrame([{'id_membro': id_membro_alt, 'status_pagamento': novo_status}])
                        st.session_state.mensalidades_df = pd.concat([st.session_state.mensalidades_df, novo_status_df], ignore_index=True)
                        update_timestamp()
                        st.success(f"Status de {membro_select} atualizado para {novo_status}!")
                        st.rerun()

        if is_admin:
            with tabs[2]: # Simulação
                st.subheader("Simulação de Receitas Mensais")
                valor_mensalidade_input = st.number_input("Valor da Mensalidade (R$)", value=VALOR_MENSALIDADE, min_value=0.0, format="%.2f")
                
                total_ativos = len(st.session_state.membros_df[st.session_state.membros_df['status'] == 'Ativo'])
                total_adimplentes = len(st.session_state.mensalidades_df[st.session_state.mensalidades_df['status_pagamento'] == 'Adimplente'])
                
                receita_potencial = total_ativos * valor_mensalidade_input
                receita_arrecadada = total_adimplentes * valor_mensalidade_input
                receita_pendente = receita_potencial - receita_arrecadada

                col1, col2, col3 = st.columns(3)
                col1.metric("Receita Potencial", f"R$ {receita_potencial:,.2f}", help=f"{total_ativos} membros ativos")
                col2.metric("Receita Arrecadada", f"R$ {receita_arrecadada:,.2f}", help=f"{total_adimplentes} adimplentes")
                col3.metric("Receita Pendente", f"R$ {receita_pendente:,.2f}", delta=f"- R$ {receita_pendente:,.2f}", delta_color="inverse")

            with tabs[3]: # Adicionar Lançamento
                # ... (código do formulário de adicionar)
                pass

    # ... (outras páginas)

    # --- RODAPÉ ---
    st.markdown("<hr>", unsafe_allow_html=True)
    last_update_str = st.session_state.last_update.strftime("%d/%m/%Y às %H:%M:%S")
    st.markdown(f"<p style='text-align: center; color: grey;'>Última atualização em: {last_update_str}</p>", unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()
