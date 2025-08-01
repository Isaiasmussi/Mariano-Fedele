# app.py
# Versão Final com Integração Firebase, Configuração Automática e Diagnóstico de Erros

import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar
from streamlit_option_menu import option_menu
from google.cloud import firestore
import json

# --- Configuração da Página ---
st.set_page_config(
    page_title="Gestão DeMolay - Mariano Fedele",
    page_icon="https://i.ibb.co/nsF1xTF0/image.jpg",
    layout="wide"
)

# --- DADOS E AUTENTICAÇÃO ---
SENHA_ADMIN = "cascao"
SENHA_VISITANTE = "zegotinha"
VALOR_MENSALIDADE = 20.00

# --- CONEXÃO COM FIREBASE ---
@st.cache_resource
def get_db_connection():
    """Conecta-se ao Firestore usando as credenciais do Streamlit Secrets."""
    try:
        creds_dict = st.secrets["firebase_credentials"]
        creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        db = firestore.Client.from_service_account_info(creds_dict)
        return db
    except Exception as e:
        st.error(f"Erro ao conectar ao Firebase: {e}")
        st.error("Verifique se o seu ficheiro .streamlit/secrets.toml está configurado corretamente com a secção [firebase_credentials].")
        # Linha de diagnóstico: mostra quais segredos o Streamlit está a ver
        st.warning(f"Segredos disponíveis encontrados: {list(st.secrets.keys())}")
        return None

db = get_db_connection()

# --- FUNÇÕES DE DADOS COM FIREBASE ---
def load_collection_to_df(collection_name):
    """Carrega uma coleção do Firestore e a converte num DataFrame."""
    if db is None: return pd.DataFrame()
    docs = db.collection(collection_name).stream()
    data = [doc.to_dict() for doc in docs]
    return pd.DataFrame(data)

def save_dataframe_to_firestore(df, collection_name, id_column):
    """Salva um DataFrame inteiro no Firestore."""
    for index, row in df.iterrows():
        doc_id = str(row[id_column])
        row_dict = row.to_dict()
        for key, value in row_dict.items():
            if isinstance(value, pd.Timestamp):
                row_dict[key] = value.isoformat()
        db.collection(collection_name).document(doc_id).set(row_dict)

def add_or_update_doc(collection_name, doc_id, data_dict):
    """Adiciona ou atualiza um documento."""
    if db is None: return
    for key, value in data_dict.items():
        if isinstance(value, pd.Timestamp):
            data_dict[key] = value.isoformat()
    db.collection(collection_name).document(str(doc_id)).set(data_dict)
    update_timestamp()

def delete_doc(collection_name, doc_id):
    """Exclui um documento."""
    if db is None: return
    db.collection(collection_name).document(str(doc_id)).delete()
    update_timestamp()

def seed_initial_data():
    """Popula a base de dados com dados de exemplo se estiver vazia."""
    st.info("Base de dados vazia. A popular com dados de exemplo...")
    
    membros_df = pd.DataFrame({
        'id_membro': [1, 2, 3, 4], 'cid': ['12345', '54321', '67890', '09876'],
        'nome': ['João da Silva', 'Carlos Pereira', 'Pedro Almeida', 'Lucas Souza'],
        'telefone': ['(51) 99999-1111', '(51) 98888-2222', '(51) 97777-3333', '(51) 96666-4444'],
        'status': ['Ativo', 'Ativo', 'Sênior', 'Ativo'],
        'email': ['joao@email.com', 'carlos@email.com', 'pedro@email.com', 'lucas@email.com']
    })
    save_dataframe_to_firestore(membros_df, "membros", "id_membro")

    eventos_df = pd.DataFrame({
        'id_evento': [101, 102, 103], 'data': pd.to_datetime(['2025-08-10', '2025-08-17', '2025-08-24']),
        'evento': ['Reunião Ordinária', 'Filantropia - Asilo', 'Cerimônia Magna de Iniciação'],
        'descricao': ['Discussão de projetos.', 'Visita e doação.', 'Iniciação de novos membros.'],
        'cor': ['#FF6347', '#4682B4', '#32CD32']
    })
    save_dataframe_to_firestore(eventos_df, "eventos", "id_evento")

    tesouraria_df = pd.DataFrame({
        'id_transacao': [1, 2, 3], 'data': pd.to_datetime(['2025-08-01', '2025-08-05', '2025-08-02']),
        'descricao': ['Taxa mensal - João', 'Compra de materiais', 'Taxa mensal - Carlos'],
        'tipo': ['Entrada', 'Saída', 'Entrada'], 'valor': [25.00, -15.50, 25.00]
    })
    save_dataframe_to_firestore(tesouraria_df, "tesouraria", "id_transacao")

    mensalidades_df = pd.DataFrame({
        'id_membro': [1, 2, 4], 'status_pagamento': ['Adimplente', 'Inadimplente', 'Adimplente']
    })
    save_dataframe_to_firestore(mensalidades_df, "mensalidades", "id_membro")

    st.success("Dados de exemplo carregados! A página será recarregada.")
    st.rerun()

def initialize_data():
    """Carrega os dados do Firestore para o session_state."""
    if db is None: return

    membros_check = db.collection("membros").limit(1).get()
    if not membros_check:
        seed_initial_data()

    st.session_state.membros_df = load_collection_to_df("membros")
    st.session_state.eventos_df = load_collection_to_df("eventos")
    st.session_state.tesouraria_df = load_collection_to_df("tesouraria")
    st.session_state.mensalidades_df = load_collection_to_df("mensalidades")
    st.session_state.presenca_df = load_collection_to_df("presenca")

    for df_name, col_name in [('eventos_df', 'data'), ('tesouraria_df', 'data')]:
        if df_name in st.session_state and not st.session_state[df_name].empty and col_name in st.session_state[df_name].columns:
            st.session_state[df_name][col_name] = pd.to_datetime(st.session_state[df_name][col_name])

    if 'projecao_extras' not in st.session_state: st.session_state.projecao_extras = {}
    if 'last_update' not in st.session_state: st.session_state.last_update = datetime.now()
    if 'clicked_event_id' not in st.session_state: st.session_state.clicked_event_id = None

def get_proximo_id(df, id_column):
    if df.empty or id_column not in df.columns or df[id_column].isnull().all():
        return 1
    return int(df[id_column].max() + 1)

def update_timestamp():
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
    if 'membros_df' not in st.session_state:
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
    )

    if selected == "Visão Geral":
        st.header("Visão Geral do Capítulo")
        # ... (código da página Visão Geral)

    elif selected == "Membros":
        st.header("Gestão de Membros")
        # ... (código da página Membros)

    elif selected == "Calendário":
        st.header("Calendário de Eventos")
        # ... (código da página Calendário)

    elif selected == "Tesouraria":
        st.header("Gestão da Tesouraria")
        # ... (código da página Tesouraria)

    elif selected == "Projetos":
        st.header("Gestão de Projetos")
        st.info("Área em desenvolvimento para gerenciar projetos filantrópicos e internos.")
        if is_admin:
            st.button("Criar Novo Projeto")

    elif selected == "Presença":
        st.header("Controle de Presença")
        # ... (código da página Presença)

    # --- RODAPÉ ---
    st.markdown("<hr>", unsafe_allow_html=True)
    last_update_str = st.session_state.last_update.strftime("%d/%m/%Y às %H:%M:%S")
    st.markdown(f"<p style='text-align: center; color: grey;'>Última atualização em: {last_update_str}</p>", unsafe_allow_html=True)
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
