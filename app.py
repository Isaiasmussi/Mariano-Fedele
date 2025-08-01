# app.py
# Versão Final com Integração Firebase, Configuração Automática e Correção de Erros

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
VALOR_MENSALIDADE = 25.00

# --- CONEXÃO COM FIREBASE ---
@st.cache_resource
def get_db_connection():
    """Conecta-se ao Firestore usando as credenciais do Streamlit Secrets."""
    try:
        creds_dict = dict(st.secrets["firebase_credentials"])
        creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        db = firestore.Client.from_service_account_info(creds_dict)
        return db
    except Exception as e:
        st.error(f"Erro ao conectar ao Firebase: {e}")
        st.error("Verifique se o seu ficheiro .streamlit/secrets.toml está configurado corretamente com a secção [firebase_credentials].")
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
    with st.spinner("Configurando a base de dados pela primeira vez..."):
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
    st.success("Dados de exemplo carregados!")
    st.session_state.seeded = True

def initialize_data():
    """Carrega os dados do Firestore para o session_state."""
    if db is None: return

    if 'seeded' not in st.session_state:
        membros_check = db.collection("membros").limit(1).get()
        if not list(membros_check):
            seed_initial_data()
        else:
            st.session_state.seeded = True

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
    st.session_state.app_initialized = True

def get_proximo_id(df, id_column):
    if df.empty or id_column not in df.columns or df[id_column].isnull().all():
        return 1
    numeric_ids = pd.to_numeric(df[id_column], errors='coerce').dropna()
    if numeric_ids.empty:
        return 1
    return int(numeric_ids.max() + 1)

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
    if 'app_initialized' not in st.session_state:
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
        col1, col2, col3 = st.columns(3)
        membros_ativos = st.session_state.membros_df[st.session_state.membros_df['status'] == 'Ativo'].shape[0] if not st.session_state.membros_df.empty else 0
        col1.metric("Membros Ativos", f"{membros_ativos}")
        hoje = pd.Timestamp.now()
        proximos_eventos = st.session_state.eventos_df[st.session_state.eventos_df['data'] >= hoje].sort_values('data') if not st.session_state.eventos_df.empty else pd.DataFrame()
        if not proximos_eventos.empty:
            prox_evento = proximos_eventos.iloc[0]
            col2.metric("Próximo Evento", prox_evento['data'].strftime('%d/%m/%Y'), prox_evento['evento'])
        else:
            col2.metric("Próximo Evento", "Nenhum")
        saldo_atual = st.session_state.tesouraria_df['valor'].sum() if not st.session_state.tesouraria_df.empty else 0
        col3.metric("Saldo da Tesouraria", f"R$ {saldo_atual:,.2f}")

    elif selected == "Membros":
        st.header("Gestão de Membros")
        tabs = st.tabs(["Visualizar", "Adicionar", "Editar / Excluir"]) if is_admin else st.tabs(["Visualizar"])
        
        with tabs[0]:
            st.dataframe(st.session_state.membros_df, use_container_width=True)

        if is_admin:
            with tabs[1]:
                with st.form("add_membro", clear_on_submit=True):
                    novo_id = get_proximo_id(st.session_state.membros_df, 'id_membro')
                    cid = st.text_input("CID (ID DeMolay)")
                    nome = st.text_input("Nome Completo")
                    tel = st.text_input("Telefone")
                    email = st.text_input("E-mail")
                    status = st.selectbox("Status", ["Ativo", "Sênior"])
                    if st.form_submit_button("Adicionar Membro"):
                        if cid and nome:
                            novo_membro_dict = {'id_membro': novo_id, 'cid': cid, 'nome': nome, 'telefone': tel, 'status': status, 'email': email}
                            add_or_update_doc("membros", novo_id, novo_membro_dict)
                            st.success("Membro adicionado!")
                            initialize_data()
                            st.rerun()
                        else:
                            st.error("CID e Nome são obrigatórios.")
            
            with tabs[2]:
                membro_nome = st.selectbox("Selecione um membro", st.session_state.membros_df['nome'], index=None, placeholder="Escolha um membro...")
                if membro_nome:
                    membro = st.session_state.membros_df[st.session_state.membros_df['nome'] == membro_nome].iloc[0]
                    with st.form("edit_membro"):
                        cid_edit = st.text_input("CID", value=membro['cid'])
                        nome_edit = st.text_input("Nome", value=membro['nome'])
                        tel_edit = st.text_input("Telefone", value=membro['telefone'])
                        email_edit = st.text_input("E-mail", value=membro['email'])
                        status_edit = st.selectbox("Status", ["Ativo", "Sênior"], index=["Ativo", "Sênior"].index(membro['status']))
                        
                        col1, col2 = st.columns(2)
                        if col1.form_submit_button("Salvar Alterações"):
                            membro_atualizado = membro.to_dict()
                            membro_atualizado.update({'cid': cid_edit, 'nome': nome_edit, 'telefone': tel_edit, 'email': email_edit, 'status': status_edit})
                            add_or_update_doc("membros", membro['id_membro'], membro_atualizado)
                            st.success("Membro atualizado!")
                            initialize_data()
                            st.rerun()
                        if col2.form_submit_button("Excluir Membro", type="primary"):
                            delete_doc("membros", membro['id_membro'])
                            st.warning("Membro excluído.")
                            initialize_data()
                            st.rerun()

    elif selected == "Calendário":
        st.header("Calendário de Eventos")
        calendar_events = []
        if not st.session_state.eventos_df.empty:
            for _, row in st.session_state.eventos_df.iterrows():
                calendar_events.append({"title": row["evento"], "start": row["data"].strftime("%Y-%m-%d"), "id": row["id_evento"], "color": row.get("cor", "#4682B4")})
        
        clicked_event_info = calendar(events=calendar_events, options={"locale": "pt-br"}, key="calendar_main")

        if is_admin and clicked_event_info and 'id' in clicked_event_info:
            st.session_state.clicked_event_id = int(clicked_event_info['id'])

        if is_admin and st.session_state.clicked_event_id:
            event_id = st.session_state.clicked_event_id
            if not st.session_state.eventos_df.empty and event_id in st.session_state.eventos_df['id_evento'].values:
                evento_data = st.session_state.eventos_df.query(f"id_evento == {event_id}").iloc[0]
                with st.expander("Editar ou Excluir Evento Selecionado", expanded=True):
                    with st.form(f"edit_event_{event_id}"):
                        st.write(f"**Editando:** {evento_data['evento']}")
                        evento_edit = st.text_input("Nome do Evento", value=evento_data['evento'])
                        data_edit = st.date_input("Data", value=pd.to_datetime(evento_data['data']))
                        cor_edit = st.color_picker("Cor do Evento", value=evento_data['cor'])
                        
                        col1, col2 = st.columns(2)
                        if col1.form_submit_button("Salvar Alterações"):
                            evento_atualizado = evento_data.to_dict()
                            evento_atualizado.update({'evento': evento_edit, 'data': pd.to_datetime(data_edit), 'cor': cor_edit})
                            add_or_update_doc("eventos", event_id, evento_atualizado)
                            st.session_state.clicked_event_id = None
                            st.success("Evento atualizado!")
                            initialize_data()
                            st.rerun()
                        if col2.form_submit_button("Excluir Evento", type="primary"):
                            delete_doc("eventos", event_id)
                            st.session_state.clicked_event_id = None
                            st.warning("Evento excluído.")
                            initialize_data()
                            st.rerun()

        if is_admin:
            with st.expander("Adicionar Novo Evento"):
                with st.form("add_evento", clear_on_submit=True):
                    novo_id = get_proximo_id(st.session_state.eventos_df, 'id_evento')
                    evento = st.text_input("Nome do Evento")
                    data = st.date_input("Data")
                    cor = st.color_picker("Cor do Evento", "#4682B4")
                    if st.form_submit_button("Adicionar"):
                        novo_evento_dict = {'id_evento': novo_id, 'data': pd.to_datetime(data), 'evento': evento, 'descricao': '', 'cor': cor}
                        add_or_update_doc("eventos", novo_id, novo_evento_dict)
                        st.success("Evento adicionado!")
                        initialize_data()
                        st.rerun()

    elif selected == "Tesouraria":
        st.header("Gestão da Tesouraria")
        
        tab_options = ["Extrato", "Adicionar Lançamento", "Controle de Mensalidades", "Projeção Financeira"] if is_admin else ["Extrato", "Controle de Mensalidades"]
        tabs = st.tabs(tab_options)
        
        with tabs[0]: # Extrato
            saldo_total = st.session_state.tesouraria_df['valor'].sum() if not st.session_state.tesouraria_df.empty else 0
            st.metric("Saldo Atual", f"R$ {saldo_total:,.2f}")
            st.dataframe(st.session_state.tesouraria_df.sort_values('data', ascending=False), use_container_width=True)
            
            if is_admin:
                with st.expander("Remover Lançamento"):
                    if not st.session_state.tesouraria_df.empty:
                        options_list = [f"{row['data'].strftime('%d/%m/%Y')} - {row['descricao']} (R$ {row['valor']:.2f})" for index, row in st.session_state.tesouraria_df.iterrows()]
                        id_map = {f"{row['data'].strftime('%d/%m/%Y')} - {row['descricao']} (R$ {row['valor']:.2f})": row['id_transacao'] for index, row in st.session_state.tesouraria_df.iterrows()}
                        
                        transacao_selecionada = st.selectbox("Selecione o lançamento para remover", options=options_list, index=None, placeholder="Escolha um lançamento...")
                        
                        if transacao_selecionada:
                            if st.button("Remover Lançamento Selecionado", type="primary"):
                                id_para_remover = id_map[transacao_selecionada]
                                delete_doc("tesouraria", id_para_remover)
                                st.success("Lançamento removido com sucesso!")
                                initialize_data()
                                st.rerun()
                    else:
                        st.info("Nenhum lançamento para remover.")

        if is_admin:
            with tabs[1]: # Adicionar Lançamento
                st.subheader("Adicionar Novo Lançamento")
                with st.form("add_transacao", clear_on_submit=True):
                    novo_id = get_proximo_id(st.session_state.tesouraria_df, 'id_transacao')
                    desc = st.text_input("Descrição")
                    data = st.date_input("Data")
                    tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
                    valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
                    if st.form_submit_button("Adicionar"):
                        valor_final = valor if tipo == "Entrada" else -valor
                        nova_transacao_dict = {'id_transacao': novo_id, 'data': pd.to_datetime(data), 'descricao': desc, 'tipo': tipo, 'valor': valor_final}
                        add_or_update_doc("tesouraria", novo_id, nova_transacao_dict)
                        st.success("Lançamento adicionado!")
                        initialize_data()
                        st.rerun()

            with tabs[2]: # Controle de Mensalidades
                membros_ativos = st.session_state.membros_df[st.session_state.membros_df['status'] == 'Ativo']
                if not membros_ativos.empty:
                    status_mensalidades = pd.merge(membros_ativos[['id_membro', 'nome']], st.session_state.mensalidades_df, on='id_membro', how='left').fillna({'status_pagamento': 'Inadimplente'})
                    st.subheader("Status das Mensalidades")
                    st.dataframe(status_mensalidades[['nome', 'status_pagamento']], use_container_width=True)
                    with st.expander("Alterar Status de Pagamento"):
                        membro_select = st.selectbox("Selecione o Membro", options=status_mensalidades['nome'], key="sel_membro_mensal")
                        novo_status = st.radio("Novo Status", ['Adimplente', 'Inadimplente'], key="rad_status_mensal")
                        if st.button("Salvar Status"):
                            id_membro_alt = int(status_mensalidades.query(f"nome == '{membro_select}'")['id_membro'].iloc[0])
                            novo_status_dict = {'id_membro': id_membro_alt, 'status_pagamento': novo_status}
                            add_or_update_doc("mensalidades", id_membro_alt, novo_status_dict)
                            st.success(f"Status de {membro_select} atualizado para {novo_status}!")
                            initialize_data()
                            st.rerun()
                else:
                    st.info("Nenhum membro ativo para gerir mensalidades.")

            with tabs[3]: # Projeção Financeira
                st.subheader("Projeção de Fluxo de Caixa")
                # ... (código da projeção, que não salva dados, apenas exibe)

    elif selected == "Projetos":
        st.header("Gestão de Projetos")
        st.info("Área em desenvolvimento para gerenciar projetos filantrópicos e internos.")
        if is_admin:
            st.button("Criar Novo Projeto")

    elif selected == "Presença":
        st.header("Controle de Presença")
        # ... (código da página Presença, que salva no Firebase)


    # --- RODAPÉ ---
    st.markdown("<hr>", unsafe_allow_html=True)
    last_update_str = st.session_state.last_update.strftime("%d/%m/%Y às %H:%M:%S")
    st.markdown(f"<p style='text-align: center; color: grey;'>Última atualização em: {last_update_str}</p>", unsafe_allow_html=True)
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
