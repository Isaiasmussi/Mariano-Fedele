# app.py
# Versão Final com Edição de Calendário e Persistência de Dados

import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from streamlit_calendar import calendar
from streamlit_option_menu import option_menu
import os

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
DATA_FILES = {
    "membros": "membros.csv",
    "eventos": "eventos.csv",
    "tesouraria": "tesouraria.csv",
    "mensalidades": "mensalidades.csv",
    "presenca": "presenca.csv"
}

# --- FUNÇÕES DE PERSISTÊNCIA DE DADOS ---
def save_data():
    """Salva todos os DataFrames do session_state em arquivos CSV."""
    st.session_state.membros_df.to_csv(DATA_FILES["membros"], index=False)
    st.session_state.eventos_df.to_csv(DATA_FILES["eventos"], index=False)
    st.session_state.tesouraria_df.to_csv(DATA_FILES["tesouraria"], index=False)
    st.session_state.mensalidades_df.to_csv(DATA_FILES["mensalidades"], index=False)
    st.session_state.presenca_df.to_csv(DATA_FILES["presenca"], index=False)
    update_timestamp()

def load_data():
    """Carrega os dados dos arquivos CSV ou cria arquivos iniciais se não existirem."""
    # Membros
    if os.path.exists(DATA_FILES["membros"]):
        st.session_state.membros_df = pd.read_csv(DATA_FILES["membros"])
    else:
        st.session_state.membros_df = pd.DataFrame({
            'id_membro': [1, 2, 3, 4], 'cid': ['12345', '54321', '67890', '09876'],
            'nome': ['João da Silva', 'Carlos Pereira', 'Pedro Almeida', 'Lucas Souza'],
            'telefone': ['(51) 99999-1111', '(51) 98888-2222', '(51) 97777-3333', '(51) 96666-4444'],
            'status': ['Ativo', 'Ativo', 'Sênior', 'Ativo'],
            'email': ['joao@email.com', 'carlos@email.com', 'pedro@email.com', 'lucas@email.com']
        })

    # Eventos
    if os.path.exists(DATA_FILES["eventos"]):
        st.session_state.eventos_df = pd.read_csv(DATA_FILES["eventos"])
        st.session_state.eventos_df['data'] = pd.to_datetime(st.session_state.eventos_df['data'])
    else:
        st.session_state.eventos_df = pd.DataFrame({
            'id_evento': [101, 102, 103], 'data': pd.to_datetime(['2025-07-28', '2025-08-09', '2025-08-16']),
            'evento': ['Reunião Ordinária', 'Filantropia - Asilo', 'Cerimônia Magna de Iniciação'],
            'descricao': ['Discussão de projetos.', 'Visita e doação.', 'Iniciação de novos membros.'],
            'cor': ['#FF6347', '#4682B4', '#32CD32']
        })

    # Tesouraria
    if os.path.exists(DATA_FILES["tesouraria"]):
        st.session_state.tesouraria_df = pd.read_csv(DATA_FILES["tesouraria"])
        st.session_state.tesouraria_df['data'] = pd.to_datetime(st.session_state.tesouraria_df['data'])
    else:
        st.session_state.tesouraria_df = pd.DataFrame({
            'id_transacao': [1, 2, 3], 'data': pd.to_datetime(['2025-07-01', '2025-07-05', '2025-07-15']),
            'descricao': ['Taxa mensal - João', 'Compra de materiais', 'Taxa mensal - Carlos'],
            'tipo': ['Entrada', 'Saída', 'Entrada'], 'valor': [20.00, -15.50, 20.00]
        })

    # Mensalidades
    if os.path.exists(DATA_FILES["mensalidades"]):
        st.session_state.mensalidades_df = pd.read_csv(DATA_FILES["mensalidades"])
    else:
        st.session_state.mensalidades_df = pd.DataFrame({
            'id_membro': [1, 2, 4], 'status_pagamento': ['Adimplente', 'Inadimplente', 'Adimplente']
        })

    # Presença
    if os.path.exists(DATA_FILES["presenca"]):
        st.session_state.presenca_df = pd.read_csv(DATA_FILES["presenca"])
    else:
        st.session_state.presenca_df = pd.DataFrame({
            'id_evento': pd.Series(dtype='int'), 'id_membro': pd.Series(dtype='int'),
            'presente': pd.Series(dtype='bool')
        })
    
    # Inicializa outros estados da sessão
    if 'projecao_extras' not in st.session_state:
        st.session_state.projecao_extras = {}
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()

def get_proximo_id(df, id_column):
    if df.empty or not df[id_column].any():
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
    # Carrega os dados na primeira vez após o login
    if 'membros_df' not in st.session_state:
        load_data()
        # Salva os arquivos iniciais se eles não existiam
        save_data()

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

    if selected == "Visão Geral":
        st.header("Visão Geral do Capítulo")
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
        tabs = st.tabs(["Visualizar", "Adicionar", "Editar / Excluir"]) if is_admin else st.tabs(["Visualizar"])
        
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
                            novo_id = get_proximo_id(st.session_state.membros_df, 'id_membro')
                            novo_membro = pd.DataFrame([{'id_membro': novo_id, 'cid': cid, 'nome': nome, 'telefone': tel, 'status': status, 'email': email}])
                            st.session_state.membros_df = pd.concat([st.session_state.membros_df, novo_membro], ignore_index=True)
                            save_data()
                            st.success("Membro adicionado!")
                            st.rerun()
                        else:
                            st.error("CID e Nome são obrigatórios.")
            
            with tabs[2]:
                membro_nome = st.selectbox("Selecione um membro", st.session_state.membros_df['nome'], index=None, placeholder="Escolha um membro...")
                if membro_nome:
                    idx = st.session_state.membros_df.index[st.session_state.membros_df['nome'] == membro_nome].tolist()[0]
                    membro = st.session_state.membros_df.loc[idx]
                    with st.form("edit_membro"):
                        cid_edit = st.text_input("CID", value=membro['cid'])
                        nome_edit = st.text_input("Nome", value=membro['nome'])
                        tel_edit = st.text_input("Telefone", value=membro['telefone'])
                        email_edit = st.text_input("E-mail", value=membro['email'])
                        status_edit = st.selectbox("Status", ["Ativo", "Sênior"], index=["Ativo", "Sênior"].index(membro['status']))
                        
                        col1, col2 = st.columns(2)
                        if col1.form_submit_button("Salvar Alterações"):
                            st.session_state.membros_df.loc[idx, ['cid', 'nome', 'telefone', 'email', 'status']] = [cid_edit, nome_edit, tel_edit, email_edit, status_edit]
                            save_data()
                            st.success("Membro atualizado!")
                            st.rerun()
                        if col2.form_submit_button("Excluir Membro", type="primary"):
                            st.session_state.membros_df = st.session_state.membros_df.drop(index=idx).reset_index(drop=True)
                            save_data()
                            st.warning("Membro excluído.")
                            st.rerun()

    elif selected == "Calendário":
        st.header("Calendário de Eventos")
        calendar_events = []
        for _, row in st.session_state.eventos_df.iterrows():
            calendar_events.append({"title": row["evento"], "start": row["data"].strftime("%Y-%m-%d"), "id": row["id_evento"], "color": row.get("cor", "#4682B4")})
        
        # --- CORREÇÃO APLICADA AQUI: Chave estática para o calendário ---
        clicked_event = calendar(events=calendar_events, options={"locale": "pt-br"}, key="calendar_main")

        if is_admin and clicked_event and 'id' in clicked_event:
            event_id = int(clicked_event['id'])
            # Garante que o evento ainda existe antes de tentar editar
            if event_id in st.session_state.eventos_df['id_evento'].values:
                evento_data = st.session_state.eventos_df.query(f"id_evento == {event_id}").iloc[0]
                
                with st.expander("Editar ou Excluir Evento Selecionado", expanded=True):
                    with st.form(f"edit_event_{event_id}"):
                        st.write(f"**Editando:** {evento_data['evento']}")
                        evento_edit = st.text_input("Nome do Evento", value=evento_data['evento'])
                        data_edit = st.date_input("Data", value=pd.to_datetime(evento_data['data']))
                        cor_edit = st.color_picker("Cor do Evento", value=evento_data['cor'])
                        
                        col1, col2 = st.columns(2)
                        if col1.form_submit_button("Salvar Alterações"):
                            idx = st.session_state.eventos_df.index[st.session_state.eventos_df['id_evento'] == event_id].tolist()[0]
                            st.session_state.eventos_df.loc[idx, ['evento', 'data', 'cor']] = [evento_edit, pd.to_datetime(data_edit), cor_edit]
                            save_data()
                            st.success("Evento atualizado!")
                            st.rerun()
                        if col2.form_submit_button("Excluir Evento", type="primary"):
                            st.session_state.eventos_df = st.session_state.eventos_df.query(f"id_evento != {event_id}").reset_index(drop=True)
                            save_data()
                            st.warning("Evento excluído.")
                            st.rerun()

        if is_admin:
            with st.expander("Adicionar Novo Evento"):
                with st.form("add_evento", clear_on_submit=True):
                    evento = st.text_input("Nome do Evento")
                    data = st.date_input("Data")
                    cor = st.color_picker("Cor do Evento", "#4682B4")
                    if st.form_submit_button("Adicionar"):
                        novo_id = get_proximo_id(st.session_state.eventos_df, 'id_evento')
                        novo_evento = pd.DataFrame([{'id_evento': novo_id, 'data': pd.to_datetime(data), 'evento': evento, 'descricao': '', 'cor': cor}])
                        st.session_state.eventos_df = pd.concat([st.session_state.eventos_df, novo_evento], ignore_index=True)
                        save_data()
                        st.success("Evento adicionado!")
                        st.rerun()

    elif selected == "Tesouraria":
        st.header("Gestão da Tesouraria")
        
        tab_options = ["Extrato", "Adicionar Lançamento", "Controle de Mensalidades", "Projeção Financeira"] if is_admin else ["Extrato", "Controle de Mensalidades"]
        tabs = st.tabs(tab_options)
        
        with tabs[0]: # Extrato
            saldo_total = st.session_state.tesouraria_df['valor'].sum()
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
                                st.session_state.tesouraria_df = st.session_state.tesouraria_df[st.session_state.tesouraria_df['id_transacao'] != id_para_remover]
                                save_data()
                                st.success("Lançamento removido com sucesso!")
                                st.rerun()
                    else:
                        st.info("Nenhum lançamento para remover.")

        if is_admin:
            with tabs[1]: # Adicionar Lançamento
                st.subheader("Adicionar Novo Lançamento")
                with st.form("add_transacao", clear_on_submit=True):
                    desc = st.text_input("Descrição")
                    data = st.date_input("Data")
                    tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
                    valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
                    if st.form_submit_button("Adicionar"):
                        valor_final = valor if tipo == "Entrada" else -valor
                        novo_id = get_proximo_id(st.session_state.tesouraria_df, 'id_transacao')
                        nova_transacao = pd.DataFrame([{'id_transacao': novo_id, 'data': pd.to_datetime(data), 'descricao': desc, 'tipo': tipo, 'valor': valor_final}])
                        st.session_state.tesouraria_df = pd.concat([st.session_state.tesouraria_df, nova_transacao], ignore_index=True)
                        save_data()
                        st.success("Lançamento adicionado!")
                        st.rerun()

            with tabs[2]: # Controle de Mensalidades
                membros_ativos = st.session_state.membros_df[st.session_state.membros_df['status'] == 'Ativo']
                status_mensalidades = pd.merge(membros_ativos[['id_membro', 'nome']], st.session_state.mensalidades_df, on='id_membro', how='left').fillna({'status_pagamento': 'Inadimplente'})
                st.subheader("Status das Mensalidades")
                st.dataframe(status_mensalidades[['nome', 'status_pagamento']], use_container_width=True)
                with st.expander("Alterar Status de Pagamento"):
                    membro_select = st.selectbox("Selecione o Membro", options=status_mensalidades['nome'], key="sel_membro_mensal")
                    novo_status = st.radio("Novo Status", ['Adimplente', 'Inadimplente'], key="rad_status_mensal")
                    if st.button("Salvar Status"):
                        id_membro_alt = status_mensalidades.query(f"nome == '{membro_select}'")['id_membro'].iloc[0]
                        st.session_state.mensalidades_df = st.session_state.mensalidades_df.query(f"id_membro != {id_membro_alt}")
                        novo_status_df = pd.DataFrame([{'id_membro': id_membro_alt, 'status_pagamento': novo_status}])
                        st.session_state.mensalidades_df = pd.concat([st.session_state.mensalidades_df, novo_status_df], ignore_index=True)
                        save_data()
                        st.success(f"Status de {membro_select} atualizado para {novo_status}!")
                        st.rerun()

            with tabs[3]: # Projeção Financeira
                st.subheader("Projeção de Fluxo de Caixa")
                today = datetime.today()
                meses_nomes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
                projecao_data = []
                saldo_atual = st.session_state.tesouraria_df['valor'].sum()
                receita_mensalidades = len(st.session_state.membros_df[st.session_state.membros_df['status'] == 'Ativo']) * VALOR_MENSALIDADE
                st.write("Adicione entradas ou saídas extras para simular cenários:")
                cols = st.columns(4)
                saldo_projetado = saldo_atual
                for i in range(today.month, 13):
                    mes_ano_key = f"{i}-{today.year}"
                    mes_nome = meses_nomes[i-1]
                    if mes_ano_key not in st.session_state.projecao_extras:
                        st.session_state.projecao_extras[mes_ano_key] = {'entradas': 0.0, 'saidas': 0.0}
                    with cols[(i-today.month) % 4]:
                        with st.container(border=True):
                            st.write(f"**{mes_nome}**")
                            st.session_state.projecao_extras[mes_ano_key]['entradas'] = st.number_input("Entradas Extras (+)", key=f"in_{mes_ano_key}", min_value=0.0, format="%.2f")
                            st.session_state.projecao_extras[mes_ano_key]['saidas'] = st.number_input("Saídas Extras (-)", key=f"out_{mes_ano_key}", min_value=0.0, format="%.2f")
                st.divider()
                st.subheader("Resultado da Projeção")
                for i in range(today.month, 13):
                    mes_ano_key = f"{i}-{today.year}"
                    mes_nome = meses_nomes[i-1]
                    entradas_extras = st.session_state.projecao_extras[mes_ano_key]['entradas']
                    saidas_extras = st.session_state.projecao_extras[mes_ano_key]['saidas']
                    saldo_final_mes = saldo_projetado + receita_mensalidades + entradas_extras - saidas_extras
                    projecao_data.append({
                        "Mês": mes_nome, "Saldo Inicial": f"R$ {saldo_projetado:,.2f}",
                        "Receita (Mensalidades)": f"R$ {receita_mensalidades:,.2f}",
                        "Entradas Extras": f"R$ {entradas_extras:,.2f}", "Saídas Extras": f"R$ {saidas_extras:,.2f}",
                        "Saldo Final Projetado": f"R$ {saldo_final_mes:,.2f}"
                    })
                    saldo_projetado = saldo_final_mes
                projecao_df = pd.DataFrame(projecao_data)
                st.dataframe(projecao_df, use_container_width=True)
        else:
             with tabs[1]:
                membros_ativos = st.session_state.membros_df[st.session_state.membros_df['status'] == 'Ativo']
                status_mensalidades = pd.merge(membros_ativos[['id_membro', 'nome']], st.session_state.mensalidades_df, on='id_membro', how='left').fillna({'status_pagamento': 'Inadimplente'})
                st.subheader("Status das Mensalidades")
                st.dataframe(status_mensalidades[['nome', 'status_pagamento']], use_container_width=True)

    elif selected == "Projetos":
        st.header("Gestão de Projetos")
        st.info("Área em desenvolvimento para gerenciar projetos filantrópicos e internos.")
        if is_admin:
            st.button("Criar Novo Projeto")

    elif selected == "Presença":
        st.header("Controle de Presença")
        evento_opts = st.session_state.eventos_df.sort_values('data', ascending=False)
        if not evento_opts.empty:
            evento_selecionado_nome = st.selectbox("Selecione um evento:", options=evento_opts['evento'])
            id_evento_selecionado = evento_opts[evento_opts['evento'] == evento_selecionado_nome]['id_evento'].iloc[0]
            membros_ja_registrados_ids = st.session_state.presenca_df[st.session_state.presenca_df['id_evento'] == id_evento_selecionado]['id_membro'].tolist()
            membros_para_chamada = st.session_state.membros_df[~st.session_state.membros_df['id_membro'].isin(membros_ja_registrados_ids)]
            if is_admin and not membros_para_chamada.empty:
                with st.form("chamada_form"):
                    st.write(f"**Registrar presença para: {evento_selecionado_nome}**")
                    presencas = {membro['id_membro']: st.checkbox(f"{membro['nome']} ({membro['status']})") for _, membro in membros_para_chamada.iterrows()}
                    if st.form_submit_button("Salvar Presenças"):
                        novas_presencas = [{'id_evento': id_evento_selecionado, 'id_membro': id_membro, 'presente': presente} for id_membro, presente in presencas.items()]
                        if novas_presencas:
                            st.session_state.presenca_df = pd.concat([st.session_state.presenca_df, pd.DataFrame(novas_presencas)], ignore_index=True)
                            save_data()
                            st.success("Presenças salvas!")
                            st.rerun()
            elif is_admin:
                st.info("Todos os membros já tiveram a presença registrada para este evento.")
            st.subheader(f"Resumo de Presença - {evento_selecionado_nome}")
            presenca_evento = st.session_state.presenca_df[st.session_state.presenca_df['id_evento'] == id_evento_selecionado]
            if not presenca_evento.empty:
                resultado = pd.merge(presenca_evento, st.session_state.membros_df, on='id_membro', how='left')
                resultado['presente'] = resultado['presente'].map({True: 'Presente ✅', False: 'Ausente ❌'})
                st.dataframe(resultado[['nome', 'status', 'presente']], use_container_width=True)
            else:
                st.warning("Nenhuma presença registrada para este evento ainda.")
        else:
            st.warning("Nenhum evento cadastrado.")

    # --- RODAPÉ ---
    st.markdown("<hr>", unsafe_allow_html=True)
    last_update_str = st.session_state.last_update.strftime("%d/%m/%Y às %H:%M:%S")
    st.markdown(f"<p style='text-align: center; color: grey;'>Última atualização em: {last_update_str}</p>", unsafe_allow_html=True)
    if st.button("Logout"):
        # Limpa todo o session_state para forçar o recarregamento dos dados na próxima vez
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
