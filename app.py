# app.py
# Para rodar este app:
# 1. Salve este código como `app.py`.
# 2. Instale as bibliotecas necessárias: pip install streamlit pandas
# 3. No terminal, execute: streamlit run app.py

import streamlit as st
import pandas as pd
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="Gestão DeMolay - Mariano Fedele",
    page_icon="⚜️",
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
            'data': pd.to_datetime(['2025-08-02', '2025-08-09', '2025-08-16']),
            'evento': ['Reunião Ordinária', 'Filantropia - Asilo', 'Cerimônia Magna de Iniciação'],
            'descricao': ['Discussão de projetos e planejamento.', 'Visita e doação de alimentos.', 'Iniciação de novos membros.']
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
            'id_evento': [101, 101, 101, 102, 102],
            'id_membro': [1, 2, 4, 1, 3],
            'presente': [True, True, False, True, True]
        })

# Chamada da função de inicialização
initialize_data()

# --- Barra Lateral de Navegação ---
st.sidebar.image("https://placehold.co/150x150/000000/FFFFFF?text=⚜️", width=100)
st.sidebar.title("Capítulo Mariano Fedele")
st.sidebar.markdown("---")

pagina_selecionada = st.sidebar.radio(
    "Navegação",
    ["Página Inicial", "Membros", "Calendário", "Tesouraria", "Controle de Presença"]
)

st.sidebar.markdown("---")
st.sidebar.info("Desenvolvido para facilitar a gestão do Capítulo.")

# --- Lógica para Exibir a Página Selecionada ---

if pagina_selecionada == "Página Inicial":
    st.title("Bem-vindo ao Sistema de Gestão do Capítulo! ⚜️")
    st.markdown("### Visão Geral")

    col1, col2, col3 = st.columns(3)
    
    membros_ativos = st.session_state.membros_df[st.session_state.membros_df['status'] == 'Ativo'].shape[0]
    col1.metric("Membros Ativos", f"{membros_ativos}")

    hoje = datetime.now()
    proximos_eventos = st.session_state.eventos_df[st.session_state.eventos_df['data'] >= hoje].sort_values('data')
    if not proximos_eventos.empty:
        prox_evento = proximos_eventos.iloc[0]
        col2.metric("Próximo Evento", prox_evento['data'].strftime('%d/%m/%Y'), prox_evento['evento'])
    else:
        col2.metric("Próximo Evento", "Nenhum", "Cadastre novos eventos")

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

    with st.expander("➕ Adicionar Novo Membro"):
        with st.form("novo_membro_form", clear_on_submit=True):
            novo_nome = st.text_input("Nome Completo")
            novo_status = st.selectbox("Status", ["Ativo", "Sênior"])
            novo_email = st.text_input("E-mail")
            
            submitted = st.form_submit_button("Adicionar Membro")
            if submitted:
                if novo_nome and novo_email:
                    novo_id = st.session_state.membros_df['id_membro'].max() + 1 if not st.session_state.membros_df.empty else 1
                    novo_membro_df = pd.DataFrame([{'id_membro': novo_id, 'nome': novo_nome, 'status': novo_status, 'email': novo_email}])
                    st.session_state.membros_df = pd.concat([st.session_state.membros_df, novo_membro_df], ignore_index=True)
                    st.success(f"Membro '{novo_nome}' adicionado com sucesso!")
                else:
                    st.error("Por favor, preencha o nome e o e-mail.")
    
    st.subheader("Lista de Membros")
    st.dataframe(st.session_state.membros_df, use_container_width=True)

elif pagina_selecionada == "Calendário":
    st.header("Gestão de Calendário")

    with st.expander("🗓️ Adicionar Novo Evento"):
        with st.form("novo_evento_form", clear_on_submit=True):
            nova_data = st.date_input("Data do Evento")
            novo_evento_nome = st.text_input("Nome do Evento")
            nova_descricao = st.text_area("Descrição do Evento")
            
            submitted = st.form_submit_button("Adicionar Evento")
            if submitted:
                if nova_data and novo_evento_nome:
                    novo_id = st.session_state.eventos_df['id_evento'].max() + 1 if not st.session_state.eventos_df.empty else 101
                    novo_evento_df = pd.DataFrame([{
                        'id_evento': novo_id,
                        'data': pd.to_datetime(nova_data),
                        'evento': novo_evento_nome,
                        'descricao': nova_descricao
                    }])
                    st.session_state.eventos_df = pd.concat([st.session_state.eventos_df, novo_evento_df], ignore_index=True)
                    st.success(f"Evento '{novo_evento_nome}' adicionado com sucesso!")
                else:
                    st.error("Por favor, preencha a data e o nome do evento.")

    st.subheader("Lista de Eventos")
    st.dataframe(st.session_state.eventos_df.sort_values('data', ascending=False), use_container_width=True)


elif pagina_selecionada == "Tesouraria":
    st.header("Gestão da Tesouraria")
    
    saldo_total = st.session_state.tesouraria_df['valor'].sum()
    st.metric("Saldo Atual", f"R$ {saldo_total:,.2f}")

    with st.expander("💸 Adicionar Lançamento Financeiro"):
        with st.form("novo_lancamento_form", clear_on_submit=True):
            data_lancamento = st.date_input("Data")
            desc_lancamento = st.text_input("Descrição")
            tipo_lancamento = st.selectbox("Tipo", ["Entrada", "Saída"])
            valor_lancamento = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

            submitted = st.form_submit_button("Adicionar Lançamento")
            if submitted:
                if desc_lancamento and valor_lancamento > 0:
                    valor_final = valor_lancamento if tipo_lancamento == "Entrada" else -valor_lancamento
                    novo_lancamento_df = pd.DataFrame([{
                        'data': pd.to_datetime(data_lancamento),
                        'descricao': desc_lancamento,
                        'tipo': tipo_lancamento,
                        'valor': valor_final
                    }])
                    st.session_state.tesouraria_df = pd.concat([st.session_state.tesouraria_df, novo_lancamento_df], ignore_index=True)
                    st.success("Lançamento adicionado com sucesso!")
                else:
                    st.error("Preencha a descrição e um valor maior que zero.")

    st.subheader("Extrato de Transações")
    st.dataframe(st.session_state.tesouraria_df.sort_values('data', ascending=False), use_container_width=True)

elif pagina_selecionada == "Controle de Presença":
    st.header("Lançamento de Presença")

    evento_opts = st.session_state.eventos_df.sort_values('data', ascending=False)
    if not evento_opts.empty:
        evento_selecionado_nome = st.selectbox(
            "Selecione um evento para lançar a presença:",
            options=evento_opts['evento']
        )
        
        id_evento_selecionado = evento_opts[evento_opts['evento'] == evento_selecionado_nome]['id_evento'].iloc[0]
        
        # Membros ativos que ainda não têm presença registrada para este evento
        membros_ja_registrados = st.session_state.presenca_df[st.session_state.presenca_df['id_evento'] == id_evento_selecionado]['id_membro']
        membros_ativos_para_chamada = st.session_state.membros_df[
            (st.session_state.membros_df['status'] == 'Ativo') &
            (~st.session_state.membros_df['id_membro'].isin(membros_ja_registrados))
        ]

        if not membros_ativos_para_chamada.empty:
            with st.form("chamada_form"):
                st.write(f"**Fazendo a chamada para: {evento_selecionado_nome}**")
                presencas = {}
                for _, membro in membros_ativos_para_chamada.iterrows():
                    presencas[membro['id_membro']] = st.checkbox(f"Presente - {membro['nome']}", key=membro['id_membro'])
                
                submitted = st.form_submit_button("Salvar Presenças")
                if submitted:
                    novas_presencas_list = []
                    for id_membro, presente in presencas.items():
                        novas_presencas_list.append({
                            'id_evento': id_evento_selecionado,
                            'id_membro': id_membro,
                            'presente': presente
                        })
                    
                    if novas_presencas_list:
                        novas_presencas_df = pd.DataFrame(novas_presencas_list)
                        st.session_state.presenca_df = pd.concat([st.session_state.presenca_df, novas_presencas_df], ignore_index=True)
                        st.success("Lista de presença salva com sucesso!")
                        st.rerun() # Atualiza a página para remover os membros da lista
                    else:
                        st.warning("Nenhuma presença foi marcada.")
        else:
            st.info("Todos os membros ativos já tiveram sua presença registrada para este evento.")

        # Exibir a lista de presença consolidada para o evento
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
