import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import os

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

# Função para perguntar à IA
def diagnosticar_com_groq(pergunta, contexto=None):
    messages = [
        {"role": "system", "content": "Você é um assistente médico. Responda com base nos documentos fornecidos (se houver). Sempre recomende consultar um médico."}
    ]
    
    if contexto:
        messages.append({"role": "user", "content": f"Documentos do paciente:\n{contexto}\n\nPergunta: {pergunta}"})
    else:
        messages.append({"role": "user", "content": pergunta})
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    return response.choices[0].message.content

# Interface do Streamlit
def main():
    st.set_page_config(page_title="DiagnosticAI", page_icon="⚕️")
    
    st.title("⚕️ DiagnosticAI")
    st.markdown("Faça perguntas médicas ou envie PDFs para análise.")
    
    uploaded_pdfs = st.file_uploader("📄 Envie seus exames (PDF)", type="pdf", accept_multiple_files=True)
    
    if uploaded_pdfs:
        texto_extraido = extract_text_from_pdfs(uploaded_pdfs)
        st.session_state["texto_clinico"] = texto_extraido
        st.subheader("📝 Conteúdo extraído dos PDFs:")
        st.text_area("Texto dos documentos", value=texto_extraido, height=200)
    
    pergunta = st.text_input("🩺 Qual é a sua dúvida médica?")
    
    if pergunta:
        contexto = st.session_state.get("texto_clinico", None)
        resposta = diagnosticar_com_groq(pergunta, contexto)
        st.subheader("🧾 Resposta da IA:")
        st.write(resposta)

if __name__ == "__main__":
    main()