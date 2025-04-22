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

# Função para interagir com a IA da Groq
def diagnosticar_com_groq(pergunta, contexto=None):
    messages = [
        {
            "role": "system",
            "content": """Você é uma inteligência artificial médica especializada..."""  # (mantido como antes)
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

# Interface principal
def main():
    st.set_page_config(page_title="DiagnosticAI", page_icon="⚕️", layout="centered")

    st.markdown("""
        <style>
        .chat-input {
            display: flex;
            align-items: center;
            margin-top: 20px;
        }
        .chat-input textarea {
            flex-grow: 1;
            resize: none;
            border-radius: 0.5rem;
            padding: 0.75rem;
            border: 1px solid #ccc;
            font-size: 1rem;
            background-color: #f8f9fa;
        }
        .chat-buttons {
            display: flex;
            flex-direction: row;
            align-items: center;
            margin-left: 10px;
        }
        .chat-buttons button, .chat-buttons label {
            background-color: #1f77b4;
            color: white;
            padding: 0.5rem 0.8rem;
            border: none;
            border-radius: 0.5rem;
            cursor: pointer;
            margin-left: 5px;
        }
        .file-input {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # Exibe logo
    st.image(LOGO_PATH, use_container_width=True)

    st.markdown("#### Obtenha pareceres médicos com ajuda da IA")
    st.markdown("Carregue arquivos clínicos (opcional) e envie sua dúvida.")

    if "texto_clinico" not in st.session_state:
        st.session_state["texto_clinico"] = ""

    # Caixa de entrada personalizada (parecida com ChatGPT)
    with st.form("form_pergunta", clear_on_submit=True):
        cols = st.columns([8, 1, 1])
        pergunta_usuario = cols[0].text_input("Digite sua pergunta médica:", label_visibility="collapsed", placeholder="Descreva seus sintomas ou dúvidas...")
        enviar = cols[1].form_submit_button("📤")
        upload = cols[2].file_uploader("📎", type="pdf", label_visibility="collapsed", accept_multiple_files=True)

    # Processar upload
    if upload:
        texto_extraido = extract_text_from_pdfs(upload)
        st.session_state["texto_clinico"] = texto_extraido

    # Processar pergunta
    if enviar and pergunta_usuario:
        contexto = st.session_state.get("texto_clinico", None)
        resposta = diagnosticar_com_groq(pergunta_usuario, contexto)
        st.markdown("### 🧾 Resposta da IA:")
        st.write(resposta)

if __name__ == "__main__":
    main()
