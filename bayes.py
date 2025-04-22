import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import os
import json
from datetime import datetime, time
import pandas as pd
import folium
from streamlit_folium import folium_static

# Caminho dinâmico da logo
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(CURRENT_DIR, "logo.png")

# Configurar chave da Groq
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Carregar dados de hospitais (simulados - em produção seria uma API ou banco de dados)
def carregar_hospitais():
    return [
        {"nome": "Hospital Geral", "lat": -23.5505, "lon": -46.6333, "tipo": "Geral", "telefone": "(11) 1234-5678"},
        {"nome": "Pronto Socorro Central", "lat": -23.5515, "lon": -46.6343, "tipo": "Emergência", "telefone": "(11) 9876-5432"},
        {"nome": "Hospital Infantil", "lat": -23.5525, "lon": -46.6353, "tipo": "Infantil", "telefone": "(11) 4567-8901"},
    ]

# Glossário médico
GLOSSARIO = {
    "hipertensão": "Pressão arterial elevada, geralmente acima de 140/90 mmHg.",
    "diabetes": "Doença metabólica caracterizada por altos níveis de glicose no sangue.",
    "ECG": "Eletrocardiograma - exame que registra a atividade elétrica do coração.",
    "hemoglobina": "Proteína nas células vermelhas do sangue que transporta oxigênio.",
    "PCR": "Proteína C-reativa - marcador de inflamação no organismo.",
    "TGO/TGP": "Enzimas hepáticas que ajudam a avaliar a saúde do fígado.",
    "HDL/LDL": "Tipos de colesterol - HDL é 'bom' colesterol, LDL é 'ruim'.",
}

# Função para extrair texto de PDFs
def extract_text_from_pdfs(uploaded_pdfs):
    text = ""
    for pdf in uploaded_pdfs:
        try:
            with fitz.open(stream=pdf.read(), filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text("text")
            st.success(f"✅ PDF '{pdf.name}' processado com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao ler o PDF '{pdf.name}': {e}")
    return text

# Função para classificar urgência
def classificar_urgencia(resposta):
    termos_vermelho = ["emergência", "imediatamente", "urgente", "grave", "pronto-socorro", "risco de vida"]
    termos_amarelo = ["avaliar", "breve", "logo", "dentro de dias", "atenção", "cuidado"]
    
    if any(termo in resposta.lower() for termo in termos_vermelho):
        return "🔴 Vermelho (Emergência - buscar atendimento imediato)"
    elif any(termo in resposta.lower() for termo in termos_amarelo):
        return "🟡 Amarelo (Urgente - buscar atendimento em breve)"
    else:
        return "🟢 Verde (Rotina - agendar consulta)"

# Função para adicionar tooltips com glossário
def adicionar_glossario(texto):
    for termo, explicacao in GLOSSARIO.items():
        if termo.lower() in texto.lower():
            texto = texto.replace(termo, f'<span title="{explicacao}">{termo}</span>')
            texto = texto.replace(termo.capitalize(), f'<span title="{explicacao}">{termo.capitalize()}</span>')
    return texto

# Função para interagir com a IA da Groq para diagnósticos
def diagnosticar_com_groq(pergunta, contexto=None):
    messages = [
        {
            "role": "system", 
            "content": """Você é uma inteligência artificial médica especializada em análise preliminar de condições de saúde. 
            Suas responsabilidades incluem:
            
            1. Analisar sintomas descritos pelo usuário com precisão e cuidado
            2. Interpretar relatórios clínicos e resultados de exames quando fornecidos
            3. Oferecer informações médicas baseadas em evidências científicas
            4. Sugerir possíveis condições relacionadas (como diagnóstico diferencial)
            5. Recomendar quando procurar atendimento médico
            6. Fornecer contatos de emergência quando necessário
            
            Restrições obrigatórias:
            - NUNCA afirme que seu diagnóstico é definitivo
            - Em casos potencialmente graves (como dor no peito, dificuldade respiratória, sangramentos intensos):
              * Recomende busca imediata de atendimento médico
              * Forneça números de telefone de emergência locais
              * Descreva sinais de alarme para observar
            - Para questões não médicas, responda apenas: "Desculpe, só posso ajudar com questões médicas"
            - Caso o arquivo não tenha relacão com medicina, avise o usuário e não processe o arquivo
            - Em questões médicas, inclua a frase: "Este é apenas um parecer preliminar - o diagnóstico definitivo requer avaliação médica profissional." como um paragrafo final
            - Mantenha tom profissional, empático e sem alarmismo desnecessário"""
        },
    ]
    
    if contexto:
        messages.append({"role": "user", "content": f"Contexto dos exames:\n{contexto}\n\nPergunta: {pergunta}"})
    else:
        messages.append({"role": "user", "content": pergunta})
    
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages
    )
    return response.choices[0].message.content

# Interface do Streamlit
def main():
    # Configuração da página com ícone personalizado
    st.set_page_config(
        page_title="DiagnosticAI",
        page_icon="⚕️",
        layout="wide"
    )
    
    # CSS personalizado
    st.markdown("""
    <style>
        .urg-red {
            background-color: #ffcccc;
            padding: 10px;
            border-radius: 5px;
            border-left: 5px solid #ff0000;
        }
        .urg-yellow {
            background-color: #ffffcc;
            padding: 10px;
            border-radius: 5px;
            border-left: 5px solid #ffcc00;
        }
        .urg-green {
            background-color: #ccffcc;
            padding: 10px;
            border-radius: 5px;
            border-left: 5px solid #00cc00;
        }
        .tooltip {
            border-bottom: 1px dotted #000;
            cursor: help;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Imagem da logo (com largura responsiva)
    st.image(LOGO_PATH, use_column_width=True)

    st.markdown("""
    <div style="text-align: center;">
        <h1>DiagnosticAI</h1>
        <p>Faça perguntas médicas para obter informações. Você pode carregar relatórios médicos ou exames em PDF para um diagnóstico mais preciso.</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar com múltiplas funcionalidades
    with st.sidebar:
        st.header("⚙️ Menu")
        
        tab1, tab2, tab3 = st.tabs(["📄 Documentos", "💊 Medicamentos", "🏥 Hospitais"])
        
        with tab1:
            uploaded_pdfs = st.file_uploader("Adicione seus PDFs clínicos", type="pdf", accept_multiple_files=True)
            
        with tab2:
            st.subheader("Lembretes de Medicamentos")
            
            if 'medicamentos' not in st.session_state:
                st.session_state.medicamentos = []
            
            with st.form("med_form"):
                nome_med = st.text_input("Nome do Medicamento")
                dosagem = st.text_input("Dosagem")
                horarios = st.multiselect("Horários", ["Manhã", "Tarde", "Noite"])
                frequencia = st.selectbox("Frequência", ["Diário", "Semanal", "Mensal"])
                submit_med = st.form_submit_button("Adicionar")
                
                if submit_med and nome_med:
                    novo_med = {
                        "nome": nome_med,
                        "dosagem": dosagem,
                        "horarios": horarios,
                        "frequencia": frequencia,
                        "adicionado_em": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    st.session_state.medicamentos.append(novo_med)
                    st.success("Medicamento adicionado!")
            
            if st.session_state.medicamentos:
                st.subheader("Seus Medicamentos")
                for i, med in enumerate(st.session_state.medicamentos):
                    with st.expander(f"{med['nome']} - {med['dosagem']}"):
                        st.write(f"**Horários:** {', '.join(med['horarios'])}")
                        st.write(f"**Frequência:** {med['frequencia']}")
                        st.write(f"**Adicionado em:** {med['adicionado_em']}")
                        if st.button(f"Remover {i}"):
                            st.session_state.medicamentos.pop(i)
                            st.rerun()
        
        with tab3:
            st.subheader("Hospitais Próximos")
            hospitais = carregar_hospitais()
            
            mapa = folium.Map(location=[-23.5505, -46.6333], zoom_start=13)
            
            for hospital in hospitais:
                folium.Marker(
                    [hospital["lat"], hospital["lon"]],
                    popup=f"<b>{hospital['nome']}</b><br>Tipo: {hospital['tipo']}<br>Tel: {hospital['telefone']}",
                    tooltip=hospital["nome"],
                    icon=folium.Icon(color="red" if hospital["tipo"] == "Emergência" else "blue")
                ).add_to(mapa)
            
            folium_static(mapa, width=300)
            
            st.write("**Lista de Hospitais:**")
            for hospital in hospitais:
                st.write(f"- {hospital['nome']} ({hospital['tipo']}) - Tel: {hospital['telefone']}")

    # Área principal
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if uploaded_pdfs:
            texto_extraido = extract_text_from_pdfs(uploaded_pdfs)
            st.session_state["texto_clinico"] = texto_extraido

        pergunta_usuario = st.text_area("🩺 Descreva seus sintomas ou faça sua pergunta médica:", height=150)

        if st.button("Obter Diagnóstico Preliminar"):
            if pergunta_usuario:
                contexto = st.session_state.get("texto_clinico", None)
                resposta = diagnosticar_com_groq(pergunta_usuario, contexto)
                
                # Classificar urgência
                urgencia = classificar_urgencia(resposta)
                
                # Adicionar glossário
                resposta_com_glossario = adicionar_glossario(resposta)
                
                # Exibir resultados
                st.markdown("### 🧾 Resposta da IA")
                
                # Container de urgência
                if "🔴 Vermelho" in urgencia:
                    st.markdown(f'<div class="urg-red"><h4>{urgencia}</h4></div>', unsafe_allow_html=True)
                elif "🟡 Amarelo" in urgencia:
                    st.markdown(f'<div class="urg-yellow"><h4>{urgencia}</h4></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="urg-green"><h4>{urgencia}</h4></div>', unsafe_allow_html=True)
                
                # Resposta com tooltips
                st.markdown(resposta_com_glossario, unsafe_allow_html=True)
                
                # Botões de ação
                st.markdown("### 📌 Ações Recomendadas")
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button("📞 Chamar Emergência (192)"):
                        st.warning("Ligue para 192 (SAMU) ou 193 (Bombeiros) em caso de emergência!")
                
                with col_btn2:
                    if st.button("🏥 Mostrar Hospitais Próximos"):
                        hospitais = carregar_hospitais()
                        mapa = folium.Map(location=[-23.5505, -46.6333], zoom_start=13)
                        
                        for hospital in hospitais:
                            folium.Marker(
                                [hospital["lat"], hospital["lon"]],
                                popup=f"<b>{hospital['nome']}</b><br>Tipo: {hospital['tipo']}<br>Tel: {hospital['telefone']}",
                                tooltip=hospital["nome"],
                                icon=folium.Icon(color="red" if hospital["tipo"] == "Emergência" else "blue")
                            ).add_to(mapa)
                        
                        folium_static(mapa, width=700)
                
                with col_btn3:
                    if st.button("💊 Adicionar Lembrete de Medicamento"):
                        st.session_state.show_med_form = True
                
                if st.session_state.get("show_med_form", False):
                    with st.form("quick_med_form"):
                        nome_med = st.text_input("Nome do Medicamento")
                        dosagem = st.text_input("Dosagem")
                        submit_med = st.form_submit_button("Salvar")
                        
                        if submit_med and nome_med:
                            novo_med = {
                                "nome": nome_med,
                                "dosagem": dosagem,
                                "horarios": ["Manhã", "Tarde", "Noite"],
                                "frequencia": "Diário",
                                "adicionado_em": datetime.now().strftime("%d/%m/%Y %H:%M")
                            }
                            if 'medicamentos' not in st.session_state:
                                st.session_state.medicamentos = []
                            st.session_state.medicamentos.append(novo_med)
                            st.success("Medicamento adicionado aos lembretes!")
                            st.session_state.show_med_form = False
                            st.rerun()
            else:
                st.warning("Por favor, descreva seus sintomas ou faça uma pergunta.")

    with col2:
        st.markdown("### 📌 Painel Rápido")
        
        st.markdown("#### 🚨 Contatos de Emergência")
        st.write("- SAMU: 192")
        st.write("- Bombeiros: 193")
        st.write("- Polícia: 190")
        st.write("- Centro de Toxicologia: 0800-722-6001")
        
        st.markdown("#### 📅 Próximos Lembretes")
        if 'medicamentos' in st.session_state and st.session_state.medicamentos:
            agora = datetime.now().time()
            proximos = []
            
            for med in st.session_state.medicamentos:
                if "Manhã" in med["horarios"] and time(6,0) <= agora < time(12,0):
                    proximos.append(f"{med['nome']} - Manhã")
                if "Tarde" in med["horarios"] and time(12,0) <= agora < time(18,0):
                    proximos.append(f"{med['nome']} - Tarde")
                if "Noite" in med["horarios"] and (time(18,0) <= agora or agora < time(6,0)):
                    proximos.append(f"{med['nome']} - Noite")
            
            if proximos:
                for item in proximos:
                    st.write(f"- {item}")
            else:
                st.write("Nenhum lembrete para este período.")
        else:
            st.write("Nenhum medicamento cadastrado.")
        
        st.markdown("#### 📚 Glossário Médico")
        termo_selecionado = st.selectbox("Buscar termo médico", list(GLOSSARIO.keys()))
        st.write(GLOSSARIO[termo_selecionado])

if __name__ == "__main__":
    main()