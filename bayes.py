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

# Função para extrair texto de PDFs clínicos
def extract_text_from_pdfs(uploaded_pdfs):
    text = ""
    for pdf in uploaded_pdfs:
        with fitz.open(stream=pdf.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text("text")
    return text

# Função para interagir com a IA da Groq para diagnósticos
def diagnosticar_com_groq(pergunta, contexto):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Você é uma inteligência artificial médica. Com base em relatórios clínicos e exames enviados pelo usuário em PDF, forneça diagnósticos preliminares ou hipóteses médicas. Seja claro, mas alerte sempre ao final, usando uma frase padrão que o diagnóstico definitivo depende de avaliação médica profissional. Em casos aparentam ser mais extremos recomende que o usuário busque atendimento médico imediato e forneca contatos de emergencia."},
            {"role": "user", "content": f"{contexto}\n\nPergunta: {pergunta}"}
        ]
    )
    return response.choices[0].message.content

# Interface do Streamlit
def main():
    st.set_page_config(page_title="⚕️ DiagnosticAI", layout="centered")

    st.title("⚕️ DiagnosticAI")
    st.markdown("Carregue relatórios médicos ou exames em PDF e faça perguntas para obter um **diagnóstico preliminar automatizado**.")

    with st.sidebar:
        st.header("📄 Upload de Arquivos")
        uploaded_pdfs = st.file_uploader("Adicione seus PDFs clínicos", type="pdf", accept_multiple_files=True)

    if uploaded_pdfs:
        texto_extraido = extract_text_from_pdfs(uploaded_pdfs)
        st.session_state["texto_clinico"] = texto_extraido
        st.success("✅ Relatórios clínicos processados com sucesso!")

    pergunta_usuario = st.text_input("🩺 Qual é a sua dúvida médica?")

    if pergunta_usuario and "texto_clinico" in st.session_state:
        resposta = diagnosticar_com_groq(pergunta_usuario, st.session_state["texto_clinico"])
        st.markdown("### 🧾 Resposta da IA:")
        st.write(resposta)

if __name__ == "__main__":
    main()
