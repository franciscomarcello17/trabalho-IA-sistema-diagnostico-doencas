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

# Números de emergência por país (nomes originais nos idiomas locais)
EMERGENCY_NUMBERS = {
    "Brasil": {  # Português
        "SAMU": "192",
        "Bombeiros": "193", 
        "Polícia Militar": "190",
        "Disque Intoxicação": "0800-722-6001",
        "CVV (Centro de Valorização da Vida)": "188"
    },
    "Portugal": {  # Português
        "Número de Emergência": "112",
        "Saúde 24": "808 24 24 24",
        "Centro de Informação Antivenenos": "808 250 143"
    },
    "United States": {  # Inglês
        "Emergency": "911",
        "Poison Control": "1-800-222-1222",
        "Suicide & Crisis Lifeline": "988"
    },
    "España": {  # Espanhol
        "Emergencias": "112",
        "Instituto Nacional de Toxicología": "915 620 420"
    },
    "United Kingdom": {  # Inglês
        "Emergency": "999",
        "NHS Non-emergency": "111",
        "National Poisons Information Service": "0344 892 0111"
    },
    "Deutschland": {  # Alemão
        "Notruf": "112",
        "Giftnotruf": "030-19240"
    },
    "France": {  # Francês
        "Urgences": "112",
        "SAMU (Service d'Aide Médicale Urgente)": "15",
        "Centre Antipoison": "01 40 05 48 48"
    },
    "Italia": {  # Italiano
        "Emergenza": "112",
        "Emergenza Sanitaria": "118",
        "Centro Antiveleni": "06 4997 7700"
    },
    "日本 (Japan)": {  # Japonês
        "救急 (Kyūkyū)": "119",
        "警察 (Keisatsu)": "110"
    },
    "Australia": {  # Inglês
        "Emergency": "000",
        "Poisons Information": "13 11 26"
    },
    "Canada": {  # Inglês/Francês
        "Emergency": "911",
        "Poison Control": "1-800-268-9017"
    },
    "Other": {
        "Local emergency service": "Check local number",
        "International emergency": "112 (works in many countries)"
    }
}

# Textos da interface por idioma
INTERFACE_TEXTS = {
    "Português (Brasil)": {
        "title": "DiagnosticAI",
        "header": "Faça perguntas médicas para obter informações. Você pode carregar relatórios médicos ou exames em PDF para um diagnóstico mais preciso.",
        "upload_label": "Adicione seus PDFs clínicos",
        "emergency_title": "📞 Números de Emergência",
        "question_placeholder": "🩺 Qual é a sua dúvida médica?",
        "response_title": "💡 Resposta da IA:",
        "sidebar_title": "📄 Upload de Arquivos (Opcional)"
    },
    "English (United States)": {
        "title": "DiagnosticAI",
        "header": "Ask medical questions to get information. You can upload medical reports or exams in PDF for more accurate diagnosis.",
        "upload_label": "Add your clinical PDFs",
        "emergency_title": "📞 Emergency Numbers",
        "question_placeholder": "🩺 What is your medical question?",
        "response_title": "💡 AI Response:",
        "sidebar_title": "📄 File Upload (Optional)"
    },
    "Español (España)": {
        "title": "DiagnosticAI",
        "header": "Haga preguntas médicas para obtener información. Puede cargar informes médicos o exámenes en PDF para un diagnóstico más preciso.",
        "upload_label": "Añada sus PDFs clínicos",
        "emergency_title": "📞 Números de Emergencia",
        "question_placeholder": "🩺 ¿Cuál es su duda médica?",
        "response_title": "💡 Respuesta de la IA:",
        "sidebar_title": "📄 Subida de Archivos (Opcional)"
    },
    "Français (France)": {
        "title": "DiagnosticAI",
        "header": "Posez des questions médicales pour obtenir des informations. Vous pouvez télécharger des rapports médicaux ou des examens au format PDF pour un diagnostic plus précis.",
        "upload_label": "Ajoutez vos PDFs cliniques",
        "emergency_title": "📞 Numéros d'Urgence",
        "question_placeholder": "🩺 Quelle est votre question médicale ?",
        "response_title": "💡 Réponse de l'IA:",
        "sidebar_title": "📄 Téléchargement de Fichiers (Optionnel)"
    },
    "Deutsch (Deutschland)": {
        "title": "DiagnosticAI",
        "header": "Stellen Sie medizinische Fragen, um Informationen zu erhalten. Sie können medizinische Berichte oder Untersuchungen im PDF-Format hochladen, um eine genauere Diagnose zu erhalten.",
        "upload_label": "Fügen Sie Ihre klinischen PDFs hinzu",
        "emergency_title": "📞 Notrufnummern",
        "question_placeholder": "🩺 Was ist Ihre medizinische Frage?",
        "response_title": "💡 KI-Antwort:",
        "sidebar_title": "📄 Dateiupload (Optional)"
    },
    "Italiano (Italia)": {
        "title": "DiagnosticAI",
        "header": "Fai domande mediche per ottenere informazioni. Puoi caricare referti medici o esami in PDF per una diagnosi più precisa.",
        "upload_label": "Aggiungi i tuoi PDF clinici",
        "emergency_title": "📞 Numeri di Emergenza",
        "question_placeholder": "🩺 Qual è la tua domanda medica?",
        "response_title": "💡 Risposta dell'IA:",
        "sidebar_title": "📄 Caricamento File (Opzionale)"
    }
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

# Função para mostrar números de emergência
def mostrar_numeros_emergencia(lang):
    st.sidebar.markdown(f"### {INTERFACE_TEXTS[lang]['emergency_title']}")
    pais_selecionado = st.sidebar.selectbox("Selecione seu país:", list(EMERGENCY_NUMBERS.keys()))
    
    for servico, numero in EMERGENCY_NUMBERS[pais_selecionado].items():
        st.sidebar.markdown(f"**{servico}:** `{numero}`")

# Função para interagir com a IA da Groq para diagnósticos
def diagnosticar_com_groq(pergunta, contexto=None, lang="Português (Brasil)"):
    system_prompt = {
        "Português (Brasil)": """Você é uma inteligência artificial médica especializada em análise preliminar de condições de saúde.""",
        "English (United States)": """You are a medical AI specialized in preliminary analysis of health conditions.""",
        "Español (España)": """Eres una inteligencia artificial médica especializada en el análisis preliminar de condiciones de salud.""",
        "Français (France)": """Vous êtes une intelligence artificielle médicale spécialisée dans l'analyse préliminaire des problèmes de santé.""",
        "Deutsch (Deutschland)": """Sie sind eine medizinische KI, die sich auf die vorläufige Analyse von Gesundheitszuständen spezialisiert hat.""",
        "Italiano (Italia)": """Sei un'IA medica specializzata nell'analisi preliminare delle condizioni di salute."""
    }.get(lang, """You are a medical AI specialized in preliminary analysis of health conditions.""")

    messages = [
        {
            "role": "system", 
            "content": system_prompt + """
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
        layout="centered"
    )
    
    # Seleção de idioma
    lang = st.sidebar.selectbox("🌐 Idioma / Language", list(INTERFACE_TEXTS.keys()))
    
    # Imagem da logo (com largura responsiva)
    st.image(LOGO_PATH, use_column_width=True)

    st.markdown(f"**{INTERFACE_TEXTS[lang]['header']}**")

    with st.sidebar:
        st.header(INTERFACE_TEXTS[lang]["sidebar_title"])
        uploaded_pdfs = st.file_uploader(
            INTERFACE_TEXTS[lang]["upload_label"], 
            type="pdf", 
            accept_multiple_files=True
        )
        
        mostrar_numeros_emergencia(lang)

    if uploaded_pdfs:
        texto_extraido = extract_text_from_pdfs(uploaded_pdfs)
        st.session_state["texto_clinico"] = texto_extraido

    pergunta_usuario = st.text_input(INTERFACE_TEXTS[lang]["question_placeholder"])

    if pergunta_usuario:
        contexto = st.session_state.get("texto_clinico", None)
        resposta = diagnosticar_com_groq(pergunta_usuario, contexto, lang)
        
        st.markdown(f"### {INTERFACE_TEXTS[lang]['response_title']}")
        st.markdown(resposta)

if __name__ == "__main__":
    main()