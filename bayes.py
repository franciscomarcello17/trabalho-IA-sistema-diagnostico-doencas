import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import os
import time
import base64
from faker import Faker  # Para dados de exemplo

# Caminho dinâmico da logo e outros assets
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(CURRENT_DIR, "logo.png")
BACKGROUND_PATH = os.path.join(CURRENT_DIR, "medical_bg.jpg")
SOUND_PATH = os.path.join(CURRENT_DIR, "notification.mp3")

# Configurar chave da Groq
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)
fake = Faker()

# ========== FUNÇÕES AVANÇADAS ==========
def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)

def set_background(image_path):
    with open(image_path, "rb") as f:
        img_data = f.read()
    b64_img = base64.b64encode(img_data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{b64_img}");
            background-size: cover;
            background-attachment: fixed;
            background-opacity: 0.1;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def typewriter_effect(text, speed=0.03):
    container = st.empty()
    current_text = ""
    for char in text:
        current_text += char
        container.markdown(f"<div style='font-family: monospace;'>{current_text}</div>", unsafe_allow_html=True)
        time.sleep(speed)
    return container

def generate_fake_patient_data():
    return {
        "Nome": fake.name(),
        "Idade": fake.random_int(min=18, max=90),
        "Sexo": fake.random_element(elements=("Masculino", "Feminino")),
        "Tipo Sanguíneo": fake.random_element(elements=("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-")),
        "Histórico": fake.text(max_nb_chars=200),
        "Medicações": ", ".join([fake.word() for _ in range(3)]),
        "Alergias": fake.random_element(elements=("Nenhuma", "Penicilina", "Amendoim", "Mariscos", "Látex"))
    }

# Função para extrair texto de PDFs com barra de progresso
def extract_text_from_pdfs(uploaded_pdfs):
    text = ""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, pdf in enumerate(uploaded_pdfs):
        try:
            status_text.text(f"Processando {pdf.name}...")
            with fitz.open(stream=pdf.read(), filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text("text")
            st.success(f"✅ PDF '{pdf.name}' processado com sucesso!")
            progress_bar.progress((i + 1) / len(uploaded_pdfs))
        except Exception as e:
            st.error(f"❌ Erro ao ler o PDF '{pdf.name}': {e}")
    
    progress_bar.empty()
    status_text.empty()
    return text

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
    
    with st.spinner('🔍 Analisando sua consulta...'):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        autoplay_audio(SOUND_PATH)  # Som de notificação quando pronto
        return response.choices[0].message.content

# ========== INTERFACE DO USUÁRIO ==========
def main():
    # Configuração da página premium
    st.set_page_config(
        page_title="DiagnosticAI Pro",
        page_icon="⚕️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Fundo personalizado
    set_background(BACKGROUND_PATH)
    
    # CSS personalizado
    st.markdown("""
        <style>
        .main-title {
            font-size: 3.5em;
            color: #2b5876;
            text-align: center;
            text-shadow: 2px 2px 4px #00000040;
            margin-bottom: 0;
        }
        .subtitle {
            font-size: 1.5em;
            color: #4e4376;
            text-align: center;
            margin-top: 0;
            margin-bottom: 30px;
        }
        .diagnostic-box {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        .emergency-box {
            background-color: rgba(255, 230, 230, 0.9);
            border-left: 5px solid #ff4444;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        .stButton>button {
            background: linear-gradient(45deg, #2b5876 0%, #4e4376 100%);
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Cabeçalho premium
    st.markdown("<h1 class='main-title'>DiagnosticAI Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Sua Assistente Médica Inteligente com Tecnologia de Ponta</p>", unsafe_allow_html=True)
    
    # Layout em colunas
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.expander("📋 Perfil do Paciente", expanded=True):
            if 'patient_data' not in st.session_state:
                st.session_state.patient_data = generate_fake_patient_data()
            
            st.write(f"**Nome:** {st.session_state.patient_data['Nome']}")
            st.write(f"**Idade:** {st.session_state.patient_data['Idade']}")
            st.write(f"**Sexo:** {st.session_state.patient_data['Sexo']}")
            st.write(f"**Tipo Sanguíneo:** {st.session_state.patient_data['Tipo Sanguíneo']}")
            st.write(f"**Alergias:** {st.session_state.patient_data['Alergias']}")
            
            if st.button("Gerar Novo Paciente"):
                st.session_state.patient_data = generate_fake_patient_data()
                st.rerun()
        
        with st.expander("📄 Upload de Exames", expanded=True):
            uploaded_pdfs = st.file_uploader("Arraste seus exames aqui", 
                                            type="pdf", 
                                            accept_multiple_files=True,
                                            help="Você pode enviar múltiplos arquivos PDF com seus exames médicos")
            
            if uploaded_pdfs:
                texto_extraido = extract_text_from_pdfs(uploaded_pdfs)
                st.session_state["texto_clinico"] = texto_extraido
                st.success(f"📊 {len(uploaded_pdfs)} exames processados com sucesso!")
        
        with st.expander("🆘 Emergências Comuns"):
            st.markdown("""
            <div class="emergency-box">
            <h4>🚑 Dor no Peito Intensa</h4>
            <p>Pode indicar infarto. Busque ajuda imediatamente.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="emergency-box">
            <h4>🧠 Dificuldade para Falar/Mover</h4>
            <p>Sinais de AVC. Cada minuto conta.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="emergency-box">
            <h4>😫 Dificuldade Respiratória</h4>
            <p>Pode ser asma grave, alergia ou COVID-19.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("📞 SAMU: 192 | Bombeiros: 193")
    
    with col2:
        st.markdown("<div class='diagnostic-box'>", unsafe_allow_html=True)
        
        # Consulta com animação
        with st.form(key='consulta_form'):
            pergunta_usuario = st.text_area("🩺 Descreva seus sintomas ou faça sua pergunta médica:", 
                                          height=150,
                                          placeholder="Ex: Tenho dor de cabeça forte há 3 dias, com visão turva...")
            
            submit_button = st.form_submit_button(label="🔍 Realizar Diagnóstico Preliminar", 
                                               use_container_width=True)
        
        if submit_button and pergunta_usuario:
            contexto = st.session_state.get("texto_clinico", None)
            
            # Área de resultados com animação
            st.markdown("### 📋 Resultado da Análise")
            with st.spinner('🧠 Processando com tecnologia de IA avançada...'):
                resposta = diagnosticar_com_groq(pergunta_usuario, contexto)
                
                # Efeito de máquina de escrever
                resposta_container = st.empty()
                typewriter_effect(resposta, speed=0.01)
                
                # Botões de ação
                st.download_button("💾 Salvar Diagnóstico", resposta, file_name="diagnostico_preliminar.txt")
                if st.button("🔄 Refinar Diagnóstico"):
                    resposta_refinada = diagnosticar_com_groq("Por favor, refine este diagnóstico: " + resposta, contexto)
                    st.write(resposta_refinada)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Seção de informações adicionais
        with st.expander("ℹ️ Sobre o DiagnosticAI Pro"):
            st.markdown("""
            **Tecnologia Avançada:**
            - Modelo Llama 3.3 70B da Groq
            - Processamento de linguagem natural de última geração
            - Análise contextual de documentos médicos
            
            **Aviso Legal:**
            Esta ferramenta não substitui avaliação médica profissional. 
            Sempre consulte um médico para diagnóstico definitivo.
            """)

if __name__ == "__main__":
    main()