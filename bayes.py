import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import os
import time
import base64
import random  # Substituindo o Faker por alternativas nativas

# Configurações de caminho - verifique se esses arquivos existem
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(CURRENT_DIR, "logo.png") if os.path.exists(os.path.join(CURRENT_DIR, "logo.png")) else None
BACKGROUND_PATH = os.path.join(CURRENT_DIR, "medical_bg.jpg") if os.path.exists(os.path.join(CURRENT_DIR, "medical_bg.jpg")) else None

# Configurar chave da Groq
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# ========== FUNÇÕES ALTERNATIVAS SEM FAKER ==========
def generate_patient_data():
    """Gera dados fictícios de paciente sem usar o Faker"""
    first_names = ["Ana", "Carlos", "Mariana", "João", "Beatriz", "Pedro", "Luísa", "Rafael"]
    last_names = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Almeida", "Pereira"]
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    allergies = ["Nenhuma", "Penicilina", "Amendoim", "Mariscos", "Látex", "Pólen", "Ácaros"]
    
    return {
        "Nome": f"{random.choice(first_names)} {random.choice(last_names)}",
        "Idade": random.randint(18, 90),
        "Sexo": random.choice(["Masculino", "Feminino"]),
        "Tipo Sanguíneo": random.choice(blood_types),
        "Alergias": random.choice(allergies),
        "Histórico": "Paciente com histórico de " + random.choice(["hipertensão", "diabetes", "asma", "alergias sazonais", "enxaqueca"]),
        "Medicações": random.choice(["Paracetamol", "Ibuprofeno", "Omeprazol", "Losartana", "Metformina"])
    }

# Função para extrair texto de PDFs com tratamento robusto
def extract_text_from_pdfs(uploaded_pdfs):
    text = ""
    if uploaded_pdfs:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, pdf in enumerate(uploaded_pdfs):
            try:
                status_text.text(f"Processando {pdf.name}... ({i+1}/{len(uploaded_pdfs)})")
                with fitz.open(stream=pdf.read(), filetype="pdf") as doc:
                    text += "\n".join([page.get_text("text") for page in doc])
                progress_bar.progress((i + 1) / len(uploaded_pdfs))
            except Exception as e:
                st.error(f"❌ Erro ao processar {pdf.name}: {str(e)}")
                continue
        
        progress_bar.empty()
        status_text.empty()
        
        if text:
            st.session_state["texto_clinico"] = text
            st.success("✅ Documentos processados com sucesso!")
    return text

# ========== INTERFACE DO USUÁRIO ==========
def main():
    # Configuração da página
    st.set_page_config(
        page_title="DiagnosticAI Pro",
        page_icon="⚕️",
        layout="centered",
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizado simplificado
    st.markdown("""
    <style>
    .main-title {
        font-size: 2.5em;
        color: #2b5876;
        text-align: center;
        margin-bottom: 0;
    }
    .diagnostic-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #2b5876;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Cabeçalho
    st.markdown("<h1 class='main-title'>DiagnosticAI Pro</h1>", unsafe_allow_html=True)
    st.markdown("Sua Assistente Médica Inteligente com Tecnologia de Ponta")
    
    # Layout principal
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.expander("📋 Perfil do Paciente", expanded=True):
            if 'patient_data' not in st.session_state:
                st.session_state.patient_data = generate_patient_data()
            
            st.write(f"**Nome:** {st.session_state.patient_data['Nome']}")
            st.write(f"**Idade:** {st.session_state.patient_data['Idade']}")
            st.write(f"**Sexo:** {st.session_state.patient_data['Sexo']}")
            st.write(f"**Tipo Sanguíneo:** {st.session_state.patient_data['Tipo Sanguíneo']}")
            st.write(f"**Alergias:** {st.session_state.patient_data['Alergias']}")
            
            if st.button("Gerar Novo Paciente"):
                st.session_state.patient_data = generate_patient_data()
                st.rerun()
        
        with st.expander("📄 Upload de Exames", expanded=True):
            uploaded_pdfs = st.file_uploader(
                "Carregue seus exames (PDF)", 
                type="pdf", 
                accept_multiple_files=True
            )
            if uploaded_pdfs:
                extract_text_from_pdfs(uploaded_pdfs)
    
    with col2:
        st.markdown("<div class='diagnostic-box'>", unsafe_allow_html=True)
        
        # Consulta médica
        pergunta_usuario = st.text_area(
            "🩺 Descreva seus sintomas ou faça sua pergunta médica:",
            height=150,
            placeholder="Ex: Tenho dor de cabeça há 3 dias que não melhora com analgésicos..."
        )
        
        if st.button("🔍 Realizar Diagnóstico Preliminar"):
            if pergunta_usuario:
                contexto = st.session_state.get("texto_clinico", None)
                
                with st.spinner('Analisando sua consulta...'):
                    try:
                        resposta = diagnosticar_com_groq(pergunta_usuario, contexto)
                        st.markdown("### 📋 Resultado da Análise")
                        st.write(resposta)
                    except Exception as e:
                        st.error(f"Erro ao processar sua consulta: {str(e)}")
            else:
                st.warning("Por favor, descreva seus sintomas antes de solicitar o diagnóstico.")
        
        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()