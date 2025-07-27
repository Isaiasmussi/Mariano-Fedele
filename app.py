# app.py
# Para rodar este app:
# 1. Salve este código como `app.py`.
# 2. Instale as bibliotecas necessárias: pip install streamlit pandas
# 3. Crie os arquivos .csv na mesma pasta: membros.csv, eventos.csv, tesouraria.csv, presenca.csv
# 4. No terminal, execute: streamlit run app.py

import streamlit as st
import pandas as pd
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="Gestão DeMolay - Mariano Fedele",
    page_icon="⚜️",
    layout="wide"
)

# --- Funções de Carregamento de Dados ---
# Usamos o cache do Streamlit para não recarregar os dados a cada interação.
@st.cache_data
def load_data():
    """Carrega todos os dados dos arquivos CSV."""
    try:
        membros_df = pd.read_csv("membros.csv")
    except FileNotFoundError:
        # Cria um DataFrame de exemplo se o arquivo não existir
        membros_df = pd.DataFrame({
            'id_membro': [1, 2, 3, 4],
            'nome': ['João da Silva', 'Carlos Pereira', 'Pedro Almeida', 'Lucas Souza'],
            'status': ['Ativo', 'Ativo', 'Sênior', 'Ativo'],
            'email': ['joao@email.com', 'carlos@email.com', 'pedro@email.com', 'lucas@email.com']
        })
        membros_df.to_csv("membros.csv", index=False)

    try:
        eventos_df = pd.read_csv("eventos.csv")
    except FileNotFoundError:
        eventos_df = pd.DataFrame({
            'id_evento': [101, 102, 103],
            'data': ['2025-08-02', '2025-08-09', '2025-08-16'],
            'evento': ['Reunião Ordinária', 'Filantropia - Asilo', 'Cerimônia Magna de Iniciação'],
            'descricao': ['Discussão de projetos e planejamento.', 'Visita e doação de alimentos.', 'Iniciação de novos membros.']
        })
        eventos_df.to_csv("eventos.csv", index=False)

    try:
        tesouraria_df = pd.read_csv("tesouraria.csv")
    except FileNotFoundError:
        tesouraria_df = pd.DataFrame({
            'data': ['2025-07-01', '2025-07-05', '2025-07-15'],
            'descricao': ['Taxa mensal - João', 'Compra de materiais para reunião', 'Taxa mensal - Carlos'],
            'tipo': ['Entrada', 'Saída', 'Entrada'],
            'valor': [20.00, -15.50, 20.00]
        })
        tesouraria_df.to_csv("tesouraria.csv", index=False)

    try:
        presenca_df = pd.read_csv("presenca.csv")
    except FileNotFoundError:
        presenca_df = pd.DataFrame({
            'id_evento': [101, 101, 101, 102, 102],
            'id_membro': [1, 2, 4, 1, 3],
            'presente': [True, True, False, True, True]
        })
        presenca_df.to_csv("presenca.csv", index=False)

    # Converte colunas de data para o tipo datetime
    eventos_df['data'] = pd.to_datetime(eventos_df['data'])
    tesouraria_df['data'] = pd.to_datetime(tesouraria_df['data'])
    return membros_df, eventos_df, tesouraria_df, presenca_df

# --- Carregando os dados ---
membros_df, eventos_df, tesouraria_df, presenca_df = load_data()


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
    
    # Card: Total de Membros Ativos
    membros_ativos = membros_df[membros_df['status'] == 'Ativo'].shape[0]
    col1.metric("Membros Ativos", f"{membros_ativos}")

    # Card: Próximo Evento
    hoje = datetime.now()
    proximos_eventos = eventos_df[eventos_df['data'] >= hoje].sort_values('data')
    if not proximos_eventos.empty:
        prox_evento = proximos_eventos.iloc[0]
        col2.metric("Próximo Evento", prox_evento['data'].strftime('%d/%m/%Y'), prox_evento['evento'])
    else:
        col2.metric("Próximo Evento", "Nenhum", "Cadastre novos eventos")

    # Card: Saldo da Tesouraria
    saldo_atual = tesouraria_df['valor'].sum()
    col3.metric("Saldo da Tesouraria", f"R$ {saldo_atual:,.2f}")

    st.markdown("---")
    st.subheader("Próximos Eventos")
    if not proximos_eventos.empty:
        st.dataframe(proximos_eventos[['data', 'evento']].rename(columns={'data': 'Data', 'evento': 'Evento'}).set_index('Data'), use_container_width=True)
    else:
        st.info("Não há eventos futuros cadastrados.")


elif pagina_selecionada == "Membros":
    st.header("Consulta de Membros")
    
    status_filtro = st.multiselect(
        "Filtrar por Status:",
        options=membros_df['status'].unique(),
        default=membros_df['status'].unique()
    )
    
    membros_filtrados = membros_df[membros_df['status'].isin(status_filtro)]
    
    st.dataframe(membros_filtrados, use_container_width=True)
    st.info(f"Total de membros exibidos: {len(membros_filtrados)}")


elif pagina_selecionada == "Calendário":
    st.header("Calendário de Eventos")
    
    st.subheader("Eventos Futuros")
    hoje = datetime.now()
    eventos_futuros = eventos_df[eventos_df['data'] >= hoje].sort_values('data')
    if not eventos_futuros.empty:
        for _, row in eventos_futuros.iterrows():
            with st.expander(f"{row['data'].strftime('%d/%m/%Y')} - {row['evento']}"):
                st.write(row['descricao'])
    else:
        st.success("Nenhum evento futuro agendado.")
        
    st.subheader("Eventos Passados")
    eventos_passados = eventos_df[eventos_df['data'] < hoje].sort_values('data', ascending=False)
    if not eventos_passados.empty:
        st.dataframe(eventos_passados, use_container_width=True)
    else:
        st.info("Nenhum evento passado registrado.")


elif pagina_selecionada == "Tesouraria":
    st.header("Controle da Tesouraria")
    
    saldo_total = tesouraria_df['valor'].sum()
    st.metric("Saldo Atual", f"R$ {saldo_total:,.2f}")
    
    st.subheader("Extrato de Transações")
    st.dataframe(tesouraria_df.sort_values('data', ascending=False), use_container_width=True)
    
    # Gráfico de Entradas vs. Saídas
    st.subheader("Análise Financeira")
    entradas = tesouraria_df[tesouraria_df['valor'] > 0]['valor'].sum()
    saidas = abs(tesouraria_df[tesouraria_df['valor'] < 0]['valor'].sum())
    
    analise_df = pd.DataFrame({
        'Tipo': ['Entradas', 'Saídas'],
        'Valor': [entradas, saidas]
    })
    
    st.bar_chart(analise_df.set_index('Tipo'))


elif pagina_selecionada == "Controle de Presença":
    st.header("Controle de Presença em Reuniões/Eventos")

    # Selecionar o evento para ver a presença
    evento_opts = eventos_df.sort_values('data', ascending=False)
    evento_selecionado_nome = st.selectbox(
        "Selecione um evento para ver a lista de presença:",
        options=evento_opts['evento']
    )

    if evento_selecionado_nome:
        id_evento_selecionado = evento_opts[evento_opts['evento'] == evento_selecionado_nome]['id_evento'].iloc[0]
        
        # Filtra a presença para o evento selecionado
        presenca_evento = presenca_df[presenca_df['id_evento'] == id_evento_selecionado]
        
        if not presenca_evento.empty:
            # Junta as informações de presença com os nomes dos membros
            resultado_presenca = pd.merge(
                presenca_evento,
                membros_df,
                on='id_membro',
                how='left'
            )
            
            # Mapeia True/False para Presente/Ausente
            resultado_presenca['presente'] = resultado_presenca['presente'].map({True: 'Presente ✅', False: 'Ausente ❌'})
            
            st.dataframe(resultado_presenca[['nome', 'status', 'presente']].rename(columns={
                'nome': 'Nome do Membro',
                'status': 'Status',
                'presente': 'Presença'
            }), use_container_width=True)

            # Calcula a porcentagem de presença
            total_presentes = resultado_presenca['presente'].value_counts().get('Presente ✅', 0)
            total_na_lista = len(resultado_presenca)
            percentual = (total_presentes / total_na_lista) * 100 if total_na_lista > 0 else 0
            st.progress(int(percentual))
            st.markdown(f"**{total_presentes} de {total_na_lista} membros compareceram ({percentual:.2f}% de presença).**")

        else:
            st.warning("Ainda não há lista de presença registrada para este evento.")


