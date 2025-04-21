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
            - SEMPRE inclua a frase: "Este é apenas um parecer preliminar - o diagnóstico definitivo requer avaliação médica presencial"
            - Em casos potencialmente graves (como dor no peito, dificuldade respiratória, sangramentos intensos):
              * Recomende busca imediata de atendimento médico
              * Forneça números de telefone de emergência locais
              * Descreva sinais de alarme para observar
            - Para questões não médicas, responda apenas: "Desculpe, só posso ajudar com questões médicas"
            - Caso o arquivo não tenha relacão com medicina, avise o usuário e não processe o arquivo
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
    # Configuração da página com ícone personalizado
    st.set_page_config(
        page_title="DiagnosticAI",
        page_icon="⚕️",
        layout="centered"
    )
    
    # Imagem da logo (com largura responsiva)
    st.image(LOGO_PATH, use_container_width=True)

    st.markdown("Faça perguntas médicas para obter informações. Você pode carregar relatórios médicos ou exames em PDF para um diagnóstico mais preciso.")

    with st.sidebar:
        st.header("📄 Upload de Arquivos (Opcional)")
        uploaded_pdfs = st.file_uploader("Adicione seus PDFs clínicos", type="pdf", accept_multiple_files=True)

    if uploaded_pdfs:
        texto_extraido = extract_text_from_pdfs(uploaded_pdfs)
        st.session_state["texto_clinico"] = texto_extraido
        st.success("✅ Relatórios clínicos processados com sucesso!")

    pergunta_usuario = st.text_input("🩺 Qual é a sua dúvida médica?")

    if pergunta_usuario:
        contexto = st.session_state.get("texto_clinico", None)
        resposta = diagnosticar_com_groq(pergunta_usuario, contexto)
        st.markdown("### 🧾 Resposta da IA:")
        st.write(resposta)

if __name__ == "__main__":
    main()