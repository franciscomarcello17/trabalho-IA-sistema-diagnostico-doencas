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
    st.set_page_config(page_title="DiagnosticAI", page_icon="⚕️", layout="centered")

    # Estilo visual tipo ChatGPT com suas cores
    st.markdown("""
    <style>
    body {
        background-color: #f5f7fa;
    }
    .main {
        background-color: white;
        border-radius: 12px;
        padding: 2rem;
    }
    .message {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 12px;
        line-height: 1.6;
    }
    .user-message {
        background-color: #eef2f7;
        border-left: 5px solid #3b82f6;
    }
    .ai-message {
        background-color: #e8f0fe;
        border-left: 5px solid #10b981;
    }
    .stTextInput>div>div>input, .stTextArea textarea {
        background-color: #eef2f7 !important;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    # Logo e título
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

    # Campo para a pergunta médica
    st.markdown("### 🩺 Digite sua dúvida médica")
    pergunta_usuario = st.text_area("Qual é sua pergunta?", height=100)

    if st.button("Enviar Pergunta"):
        contexto = st.session_state.get("texto_clinico", None)
        resposta = diagnosticar_com_groq(pergunta_usuario, contexto)

        # Mostrar pergunta como uma "mensagem"
        st.markdown(f"""
        <div class="message user-message">
            <strong>Você perguntou:</strong><br>{pergunta_usuario}
        </div>
        """, unsafe_allow_html=True)

        # Mostrar resposta como "mensagem da IA"
        st.markdown(f"""
        <div class="message ai-message">
            <strong>Resposta da IA:</strong><br>{resposta}
        </div>
        """, unsafe_allow_html=True)

    # Rodapé
    st.markdown("---")
    st.markdown("""
    <center><small>⚠️ As respostas fornecidas são apenas pareceres preliminares e <strong>não substituem avaliação médica profissional</strong>.</small></center>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
