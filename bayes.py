import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import os

# Caminho dinâmico da logo
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(CURRENT_DIR, "logo.png")

# Configurar chave da Groq
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

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
            - Em questões médicas, inclua a frase: "Este é apenas um parecer preliminar - o diagnóstico definitivo requer avaliação médica profissional." como um parágrafo final
            - Mantenha tom profissional, empático e sem alarmismo desnecessário"""
        },
    ]
    
    if contexto:
        messages.append({"role": "user", "content": f"Contexto dos exames:\n{contexto}\n\nPergunta: {pergunta}"})
    else:
        messages.append({"role": "user", "content": pergunta})
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return response.choices[0].message.content

# Interface do Streamlit
def main():
    # Configuração da página
    st.set_page_config(
        page_title="DiagnosticAI",
        page_icon="⚕️",
        layout="centered"
    )

    # Estilo customizado
    st.markdown("""
    <style>
    .reportview-container {
        background-color: #f5f7fa;
    }
    .main {
        background-color: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .stTextInput>div>div>input, .stTextArea textarea {
        background-color: #eef2f7;
    }
    .pergunta-container {
        position: relative;
    }
    .enviar-btn {
        position: absolute;
        bottom: 10px;
        right: 10px;
        border: none;
        background-color: #3b82f6;
        color: white;
        border-radius: 50%;
        width: 38px;
        height: 38px;
        cursor: pointer;
        font-size: 20px;
    }
    .enviar-btn:hover {
        background-color: #2563eb;
    }
    .centered-title {
        text-align: center;
        font-weight: 600;
        font-size: 22px;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # Logo
    with st.container():
        st.image(LOGO_PATH, use_container_width=True)

    # Upload na barra lateral
    with st.sidebar:
        st.header("📄 Upload de Arquivos")
        uploaded_pdfs = st.file_uploader("Adicione relatórios ou exames clínicos (PDF)", type="pdf", accept_multiple_files=True)

    # Processar PDFs enviados
    if uploaded_pdfs:
        texto_extraido = extract_text_from_pdfs(uploaded_pdfs)
        st.session_state["texto_clinico"] = texto_extraido
        with st.expander("📄 Visualizar texto clínico extraído"):
            st.text(texto_extraido)

    # Título centralizado
    st.markdown('<div class="centered-title">🩺 Digite sua dúvida médica</div>', unsafe_allow_html=True)

    # Input com botão dentro
    with st.form("form_pergunta", clear_on_submit=True):
        st.markdown('<div class="pergunta-container">', unsafe_allow_html=True)
        pergunta_usuario = st.text_area("", height=100, placeholder="Digite sua pergunta aqui...")
        st.markdown('<button class="enviar-btn" type="submit">↑</button>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        submitted = st.form_submit_button("Enviar", type="primary")

    if submitted and pergunta_usuario.strip():
        contexto = st.session_state.get("texto_clinico", None)
        resposta = diagnosticar_com_groq(pergunta_usuario, contexto)
        st.markdown("### 🧾 Resposta da IA:")
        st.markdown(f"""
        <div style="background-color: #e8f0fe; padding: 1rem; border-radius: 10px; border-left: 5px solid #3b82f6;">
        {resposta}
        </div>
        """, unsafe_allow_html=True)

    # Rodapé
    st.markdown("---")
    st.markdown("""
    <center><small>⚠️ As respostas fornecidas são apenas pareceres preliminares e <strong>não substituem avaliação médica profissional</strong>.</small></center>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
