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

# Define os usuários administradores e a senha. Em um app real, use segredos!
ADMIN_USERS = {
    "admin": "demolay123",
    "mestreconselheiro": "demolay123",
    "escrivao": "demolay123"
}

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
            'data': pd.to_datetime(['2025-07-01', '2025-07-05', '2025-07-15']),
            'descricao': ['Taxa mensal - João', 'Compra de materiais', 'Taxa mensal - Carlos'],
            'tipo': ['Entrada', 'Saída', 'Entrada'],
            'valor': [20.00, -15.50, 20.00]
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
    """Exibe a tela de login e gerencia a autenticação."""
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

    is_admin = st.session_state.role == "admin"

    if selected == "Visão Geral":
        st.header("Visão Geral do Capítulo ⚜️")
        col1, col2, col3 = st.columns(3)
        membros_ativos = st.session_state.membros_df[st.session_state.membros_df['status'] == 'Ativo'].shape[0]
        col1.metric("Membros Ativos", f"{membros_ativos}")
        hoje = pd.Timestamp.now()
        proximos_eventos = st.session_state.eventos_df[st.session_state.eventos_df['data'] >= hoje].sort_values('data')
        if not proximos_eventos.empty:
            prox_evento = proximos_eventos.iloc[0]
            col2.metric("Próximo Evento", prox_evento['data'].strftime('%d/%m/%Y'), prox_evento['evento'])
        else:
            col2.metric("Próximo Evento", "Nenhum")
        saldo_atual = st.session_state.tesouraria_df['valor'].sum()
        col3.metric("Saldo da Tesouraria", f"R$ {saldo_atual:,.2f}")

    elif selected == "Membros":
        st.header("Gestão de Membros")
        tabs = st.tabs(["Visualizar", "➕ Adicionar", "✏️ Editar / Excluir"]) if is_admin else st.tabs(["Visualizar"])
        
        with tabs[0]:
            st.dataframe(st.session_state.membros_df, use_container_width=True)

        if is_admin:
            with tabs[1]:
                with st.form("add_membro", clear_on_submit=True):
                    cid = st.text_input("CID (ID DeMolay)")
                    nome = st.text_input("Nome Completo")
                    tel = st.text_input("Telefone")
                    email = st.text_input("E-mail")
                    status = st.selectbox("Status", ["Ativo", "Sênior"])
                    if st.form_submit_button("Adicionar Membro"):
                        if cid and nome:
                            novo_id = st.session_state.membros_df['id_membro'].max() + 1
                            novo_membro = pd.DataFrame([{'id_membro': novo_id, 'cid': cid, 'nome': nome, 'telefone': tel, 'status': status, 'email': email}])
                            st.session_state.membros_df = pd.concat([st.session_state.membros_df, novo_membro], ignore_index=True)
                            update_timestamp()
                            st.success("Membro adicionado!")
                            st.rerun()
                        else:
                            st.error("CID e Nome são obrigatórios.")
            
            with tabs[2]:
                membro_nome = st.selectbox("Selecione um membro para editar", st.session_state.membros_df['nome'], index=None, placeholder="Escolha um membro...")
                if membro_nome:
                    idx = st.session_state.membros_df.index[st.session_state.membros_df['nome'] == membro_nome].tolist()[0]
                    membro = st.session_state.membros_df.loc[idx]
                    with st.form("edit_membro"):
                        cid = st.text_input("CID", value=membro['cid'])
                        nome = st.text_input("Nome", value=membro['nome'])
                        tel = st.text_input("Telefone", value=membro['telefone'])
                        email = st.text_input("E-mail", value=membro['email'])
                        status = st.selectbox("Status", ["Ativo", "Sênior"], index=["Ativo", "Sênior"].index(membro['status']))
                        
                        col1, col2 = st.columns(2)
                        if col1.form_submit_button("Salvar Alterações"):
                            st.session_state.membros_df.loc[idx] = [membro['id_membro'], cid, nome, tel, status, email]
                            update_timestamp()
                            st.success("Membro atualizado!")
                            st.rerun()
                        if col2.form_submit_button("Excluir Membro", type="primary"):
                            st.session_state.membros_df = st.session_state.membros_df.drop(index=idx).reset_index(drop=True)
                            update_timestamp()
                            st.warning("Membro excluído.")
                            st.rerun()

    elif selected == "Calendário":
        st.header("Calendário de Eventos")
        calendar_events = []
        for _, row in st.session_state.eventos_df.iterrows():
            calendar_events.append({"title": row["evento"], "start": row["data"].strftime("%Y-%m-%d"), "color": row.get("cor", "#4682B4")})
        calendar(events=calendar_events, options={"locale": "pt-br"})
        if is_admin:
            with st.expander("🗓️ Adicionar Novo Evento"):
                # Formulário para adicionar evento aqui...
                pass

    elif selected == "Projetos":
        st.header("Gestão de Projetos")
        st.info("Área em desenvolvimento para gerenciar projetos filantrópicos e internos.")
        if is_admin:
            st.button("Criar Novo Projeto")
    
    # --- RODAPÉ ---
    st.markdown("<hr>", unsafe_allow_html=True)
    last_update_str = st.session_state.last_update.strftime("%d/%m/%Y às %H:%M:%S")
    st.markdown(f"<p style='text-align: center; color: grey;'>Última atualização em: {last_update_str}</p>", unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()
