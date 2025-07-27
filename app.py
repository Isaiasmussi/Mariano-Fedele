# app.py
# Para rodar este app:
# 1. Salve este código como `app.py`.
# 2. Crie um arquivo `requirements.txt` com:
#    streamlit
#    pandas
#    streamlit-calendar
# 3. Instale as bibliotecas: pip install -r requirements.txt
# 4. No terminal, execute: streamlit run app.py

import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar # Importa o novo componente de calendário

# --- Configuração da Página ---
st.set_page_config(
    page_title="Gestão DeMolay - Mariano Fedele",
    page_icon="https://i.ibb.co/nsF1xTF0/image.jpg", # Icone da página (URL CORRIGIDA)
    layout="wide"
)

# --- Inicialização dos Dados no Estado da Sessão ---
def initialize_data():
    """Inicializa os DataFrames no st.session_state se eles não existirem."""
    if 'membros_df' not in st.session_state:
        st.session_state.membros_df = pd.DataFrame({
            'id_membro': [1, 2, 3, 4],
            'nome': ['João da Silva', 'Carlos Pereira', 'Pedro Almeida', 'Lucas Souza'],
            'status': ['Ativo', 'Ativo', 'Sênior', 'Ativo'],
            'email': ['joao@email.com', 'carlos@email.com', 'pedro@email.com', 'lucas@email.com']
        })

    if 'eventos_df' not in st.session_state:
        st.session_state.eventos_df = pd.DataFrame({
            'id_evento': [101, 102, 103],
            'data': pd.to_datetime(['2025-07-28', '2025-08-09', '2025-08-16']),
            'evento': ['Reunião Ordinária', 'Filantropia - Asilo', 'Cerimônia Magna de Iniciação'],
            'descricao': ['Discussão de projetos e planejamento.', 'Visita e doação de alimentos.', 'Iniciação de novos membros.'],
            'cor': ['#FF6347', '#4682B4', '#32CD32'] # Cores para os eventos
        })

    if 'tesouraria_df' not in st.session_state:
        st.session_state.tesouraria_df = pd.DataFrame({
            'data': pd.to_datetime(['2025-07-01', '2025-07-05', '2025-07-15']),
            'descricao': ['Taxa mensal - João', 'Compra de materiais para reunião', 'Taxa mensal - Carlos'],
            'tipo': ['Entrada', 'Saída', 'Entrada'],
            'valor': [20.00, -15.50, 20.00]
        })

    if 'presenca_df' not in st.session_state:
        st.session_state.presenca_df = pd.DataFrame({
            'id_evento': pd.Series(dtype='int'),
            'id_membro': pd.Series(dtype='int'),
            'presente': pd.Series(dtype='bool')
        })


# Chamada da função de inicialização
initialize_data()

# --- Barra Lateral de Navegação ---
# --- CORREÇÃO APLICADA AQUI (URL e parâmetro) ---
st.sidebar.image("https://i.ibb.co/nsF1xTF0/image.jpg", use_container_width=True)
st.sidebar.title("Capítulo Mariano Fedele")
st.sidebar.markdown("---")

pagina_selecionada = st.sidebar.radio(
    "Navegação",
    ["Página Inicial", "Membros", "Calendário", "Tesouraria", "Controle de Presença"]
)

st.sidebar.markdown("---")
st.sidebar.info("Desenvolvido para facilitar a gestão do Capítulo.")

# --- Funções Auxiliares ---
def get_proximo_id(df, id_column):
    """Gera um novo ID único para um DataFrame."""
    if df.empty or df[id_column].max() != df[id_column].max(): # Checa se está vazio ou se o max é NaN
        return 1
    return int(df[id_column].max() + 1)

# --- Lógica das Páginas ---

if pagina_selecionada == "Página Inicial":
    st.title("Bem-vindo ao Sistema de Gestão do Capítulo! ⚜️")
    st.markdown("### Visão Geral")

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
    st.markdown("---")
    st.subheader("Próximos Eventos")
    if not proximos_eventos.empty:
        st.dataframe(proximos_eventos[['data', 'evento']].rename(columns={'data': 'Data', 'evento': 'Evento'}).set_index('Data'), use_container_width=True)
    else:
        st.info("Não há eventos futuros cadastrados.")

elif pagina_selecionada == "Membros":
    st.header("Gestão de Membros")

    tab1, tab2, tab3 = st.tabs(["Visualizar Membros", "➕ Adicionar Membro", "✏️ Editar / Excluir Membro"])

    with tab1:
        st.subheader("Lista de Membros")
        st.dataframe(st.session_state.membros_df, use_container_width=True)

    with tab2:
        st.subheader("Adicionar Novo Membro")
        with st.form("novo_membro_form", clear_on_submit=True):
            novo_nome = st.text_input("Nome Completo")
            novo_status = st.selectbox("Status", ["Ativo", "Sênior"], key="add_status")
            novo_email = st.text_input("E-mail")
            if st.form_submit_button("Adicionar Membro"):
                if novo_nome and novo_email:
                    novo_id = get_proximo_id(st.session_state.membros_df, 'id_membro')
                    novo_membro_df = pd.DataFrame([{'id_membro': novo_id, 'nome': novo_nome, 'status': novo_status, 'email': novo_email}])
                    st.session_state.membros_df = pd.concat([st.session_state.membros_df, novo_membro_df], ignore_index=True)
                    st.success(f"Membro '{novo_nome}' adicionado!")
                    st.rerun()
                else:
                    st.error("Nome e E-mail são obrigatórios.")

    with tab3:
        st.subheader("Editar ou Excluir Membro")
        if not st.session_state.membros_df.empty:
            membro_selecionado_nome = st.selectbox(
                "Selecione um membro para editar",
                options=st.session_state.membros_df['nome'],
                index=None,
                placeholder="Escolha um membro..."
            )
            if membro_selecionado_nome:
                membro_idx = st.session_state.membros_df.index[st.session_state.membros_df['nome'] == membro_selecionado_nome].tolist()[0]
                membro_data = st.session_state.membros_df.loc[membro_idx]

                with st.form("edit_membro_form"):
                    st.write(f"Editando: **{membro_data['nome']}**")
                    nome_edit = st.text_input("Nome", value=membro_data['nome'])
                    status_edit = st.selectbox("Status", ["Ativo", "Sênior"], index=["Ativo", "Sênior"].index(membro_data['status']))
                    email_edit = st.text_input("E-mail", value=membro_data['email'])

                    col_edit, col_delete = st.columns(2)
                    if col_edit.form_submit_button("Salvar Alterações", use_container_width=True):
                        st.session_state.membros_df.loc[membro_idx, ['nome', 'status', 'email']] = [nome_edit, status_edit, email_edit]
                        st.success("Membro atualizado com sucesso!")
                        st.rerun()
                    
                    if col_delete.form_submit_button("Excluir Membro", type="primary", use_container_width=True):
                        st.session_state.membros_df = st.session_state.membros_df.drop(index=membro_idx).reset_index(drop=True)
                        st.warning(f"Membro '{membro_selecionado_nome}' foi excluído.")
                        st.rerun()
        else:
            st.info("Nenhum membro cadastrado para editar.")


elif pagina_selecionada == "Calendário":
    st.header("Calendário de Eventos")

    calendar_events = []
    for _, row in st.session_state.eventos_df.iterrows():
        calendar_events.append({
            "title": row["evento"],
            "start": row["data"].strftime("%Y-%m-%d"),
            "end": row["data"].strftime("%Y-%m-%d"),
            "color": row.get("cor", "#4682B4"),
        })
    
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay",
        },
        "initialView": "dayGridMonth",
        "locale": "pt-br",
    }

    calendar(events=calendar_events, options=calendar_options, key="calendar")

    with st.expander("🗓️ Adicionar Novo Evento"):
        with st.form("novo_evento_form", clear_on_submit=True):
            novo_evento_nome = st.text_input("Nome do Evento")
            nova_data = st.date_input("Data do Evento")
            nova_descricao = st.text_area("Descrição do Evento")
            nova_cor = st.color_picker("Cor do Evento", "#4682B4")
            
            if st.form_submit_button("Adicionar Evento"):
                if nova_data and novo_evento_nome:
                    novo_id = get_proximo_id(st.session_state.eventos_df, 'id_evento')
                    novo_evento_df = pd.DataFrame([{'id_evento': novo_id, 'data': pd.to_datetime(nova_data), 'evento': novo_evento_nome, 'descricao': nova_descricao, 'cor': nova_cor}])
                    st.session_state.eventos_df = pd.concat([st.session_state.eventos_df, novo_evento_df], ignore_index=True)
                    st.success(f"Evento '{novo_evento_nome}' adicionado!")
                    st.rerun()
                else:
                    st.error("Data e Nome do evento são obrigatórios.")

elif pagina_selecionada == "Tesouraria":
    st.header("Gestão da Tesouraria")
    saldo_total = st.session_state.tesouraria_df['valor'].sum()
    st.metric("Saldo Atual", f"R$ {saldo_total:,.2f}")

    with st.expander("💸 Adicionar Lançamento"):
        with st.form("novo_lancamento_form", clear_on_submit=True):
            data_lancamento = st.date_input("Data")
            desc_lancamento = st.text_input("Descrição")
            tipo_lancamento = st.selectbox("Tipo", ["Entrada", "Saída"])
            valor_lancamento = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            if st.form_submit_button("Adicionar Lançamento"):
                if desc_lancamento and valor_lancamento > 0:
                    valor_final = valor_lancamento if tipo_lancamento == "Entrada" else -valor_lancamento
                    novo_lancamento_df = pd.DataFrame([{'data': pd.to_datetime(data_lancamento), 'descricao': desc_lancamento, 'tipo': tipo_lancamento, 'valor': valor_final}])
                    st.session_state.tesouraria_df = pd.concat([st.session_state.tesouraria_df, novo_lancamento_df], ignore_index=True)
                    st.success("Lançamento adicionado!")
                    st.rerun()
                else:
                    st.error("Descrição e um valor maior que zero são obrigatórios.")
    st.subheader("Extrato de Transações")
    st.dataframe(st.session_state.tesouraria_df.sort_values('data', ascending=False), use_container_width=True)


elif pagina_selecionada == "Controle de Presença":
    st.header("Lançamento de Presença")
    evento_opts = st.session_state.eventos_df.sort_values('data', ascending=False)
    if not evento_opts.empty:
        evento_selecionado_nome = st.selectbox("Selecione um evento:", options=evento_opts['evento'])
        id_evento_selecionado = evento_opts[evento_opts['evento'] == evento_selecionado_nome]['id_evento'].iloc[0]
        
        membros_ja_registrados_df = st.session_state.presenca_df[st.session_state.presenca_df['id_evento'] == id_evento_selecionado]
        membros_ja_registrados_ids = membros_ja_registrados_df['id_membro'].tolist()
        
        membros_para_chamada = st.session_state.membros_df[~st.session_state.membros_df['id_membro'].isin(membros_ja_registrados_ids)]

        if not membros_para_chamada.empty:
            with st.form("chamada_form"):
                st.write(f"**Fazendo a chamada para: {evento_selecionado_nome}**")
                presencas = {}
                for _, membro in membros_para_chamada.iterrows():
                    presencas[membro['id_membro']] = st.checkbox(f"{membro['nome']} ({membro['status']})", key=membro['id_membro'])
                
                if st.form_submit_button("Salvar Presenças"):
                    novas_presencas_list = [{'id_evento': id_evento_selecionado, 'id_membro': id_membro, 'presente': presente} for id_membro, presente in presencas.items()]
                    if novas_presencas_list:
                        novas_presencas_df = pd.DataFrame(novas_presencas_list)
                        st.session_state.presenca_df = pd.concat([st.session_state.presenca_df, novas_presencas_df], ignore_index=True)
                        st.success("Lista de presença salva!")
                        st.rerun()
        else:
            st.info("Todos os membros já tiveram sua presença registrada para este evento.")

        st.subheader(f"Resumo de Presença - {evento_selecionado_nome}")
        presenca_evento = st.session_state.presenca_df[st.session_state.presenca_df['id_evento'] == id_evento_selecionado]
        if not presenca_evento.empty:
            resultado_presenca = pd.merge(presenca_evento, st.session_state.membros_df, on='id_membro', how='left')
            resultado_presenca['presente'] = resultado_presenca['presente'].map({True: 'Presente ✅', False: 'Ausente ❌'})
            st.dataframe(resultado_presenca[['nome', 'status', 'presente']], use_container_width=True)
        else:
            st.warning("Nenhuma presença registrada para este evento ainda.")
    else:
        st.warning("Nenhum evento cadastrado. Adicione eventos na página 'Calendário' primeiro.")
