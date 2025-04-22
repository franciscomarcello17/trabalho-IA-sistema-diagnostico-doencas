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

# Dicionário de países por idioma (para mapear automaticamente os números de emergência)
COUNTRIES_BY_LANGUAGE = {
    "Português (Brasil)": "Brasil",
    "Português (Portugal)": "Portugal",
    "English (United States)": "United States",
    "English (United Kingdom)": "United Kingdom",
    "Español (España)": "España",
    "Français (France)": "France",
    "Deutsch (Deutschland)": "Deutschland",
    "Italiano (Italia)": "Italia",
    "日本語 (Japan)": "日本 (Japan)",
    "English (Australia)": "Australia",
    "English (Canada)": "Canada"
}

# Números de emergência por país (nomes originais nos idiomas locais)
EMERGENCY_NUMBERS = {
    "Brasil": {
        "SAMU": "192",
        "Bombeiros": "193", 
        "Polícia Militar": "190",
        "Disque Intoxicação": "0800-722-6001",
        "CVV (Centro de Valorização da Vida)": "188"
    },
    "Portugal": {
        "Número de Emergência": "112",
        "Saúde 24": "808 24 24 24",
        "Centro de Informação Antivenenos": "808 250 143"
    },
    "United States": {
        "Emergency": "911",
        "Poison Control": "1-800-222-1222",
        "Suicide & Crisis Lifeline": "988"
    },
    "United Kingdom": {
        "Emergency": "999",
        "NHS Non-emergency": "111",
        "National Poisons Information Service": "0344 892 0111"
    },
    "España": {
        "Emergencias": "112",
        "Instituto Nacional de Toxicología": "915 620 420"
    },
    "Deutschland": {
        "Notruf": "112",
        "Giftnotruf": "030-19240"
    },
    "France": {
        "Urgences": "112",
        "SAMU (Service d'Aide Médicale Urgente)": "15",
        "Centre Antipoison": "01 40 05 48 48"
    },
    "Italia": {
        "Emergenza": "112",
        "Emergenza Sanitaria": "118",
        "Centro Antiveleni": "06 4997 7700"
    },
    "日本 (Japan)": {
        "救急 (Kyūkyū)": "119",
        "警察 (Keisatsu)": "110"
    },
    "Australia": {
        "Emergency": "000",
        "Poisons Information": "13 11 26"
    },
    "Canada": {
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
        "select_country": "Selecione seu país:",
        "question_placeholder": "🩺 Qual é a sua dúvida médica?",
        "response_title": "💡 Resposta da IA:",
        "sidebar_title": "📄 Upload de Arquivos (Opcional)",
        "pdf_success": "✅ PDF '{}' processado com sucesso!",
        "pdf_error": "❌ Erro ao ler o PDF '{}': {}",
        "select_language": "🌐 Idioma"
    },
    "Português (Portugal)": {
        "title": "DiagnosticAI",
        "header": "Faça perguntas médicas para obter informações. Pode carregar relatórios médicos ou exames em PDF para um diagnóstico mais preciso.",
        "upload_label": "Adicione os seus PDFs clínicos",
        "emergency_title": "📞 Números de Emergência",
        "select_country": "Selecione o seu país:",
        "question_placeholder": "🩺 Qual é a sua dúvida médica?",
        "response_title": "💡 Resposta da IA:",
        "sidebar_title": "📄 Carregamento de Ficheiros (Opcional)",
        "pdf_success": "✅ PDF '{}' processado com sucesso!",
        "pdf_error": "❌ Erro ao ler o PDF '{}': {}",
        "select_language": "🌐 Idioma"
    },
    "English (United States)": {
        "title": "DiagnosticAI",
        "header": "Ask medical questions to get information. You can upload medical reports or exams in PDF for more accurate diagnosis.",
        "upload_label": "Add your clinical PDFs",
        "emergency_title": "📞 Emergency Numbers",
        "select_country": "Select your country:",
        "question_placeholder": "🩺 What is your medical question?",
        "response_title": "💡 AI Response:",
        "sidebar_title": "📄 File Upload (Optional)",
        "pdf_success": "✅ PDF '{}' processed successfully!",
        "pdf_error": "❌ Error reading PDF '{}': {}",
        "select_language": "🌐 Language"
    },
    "English (United Kingdom)": {
        "title": "DiagnosticAI",
        "header": "Ask medical questions to get information. You can upload medical reports or exams in PDF for more accurate diagnosis.",
        "upload_label": "Add your clinical PDFs",
        "emergency_title": "📞 Emergency Numbers",
        "select_country": "Select your country:",
        "question_placeholder": "🩺 What is your medical question?",
        "response_title": "💡 AI Response:",
        "sidebar_title": "📄 File Upload (Optional)",
        "pdf_success": "✅ PDF '{}' processed successfully!",
        "pdf_error": "❌ Error reading PDF '{}': {}",
        "select_language": "🌐 Language"
    },
    "Español (España)": {
        "title": "DiagnosticAI",
        "header": "Haga preguntas médicas para obtener información. Puede cargar informes médicos o exámenes en PDF para un diagnóstico más preciso.",
        "upload_label": "Añada sus PDFs clínicos",
        "emergency_title": "📞 Números de Emergencia",
        "select_country": "Seleccione su país:",
        "question_placeholder": "🩺 ¿Cuál es su duda médica?",
        "response_title": "💡 Respuesta de la IA:",
        "sidebar_title": "📄 Subida de Archivos (Opcional)",
        "pdf_success": "✅ PDF '{}' procesado con éxito!",
        "pdf_error": "❌ Error al leer el PDF '{}': {}",
        "select_language": "🌐 Idioma"
    },
    "Français (France)": {
        "title": "DiagnosticAI",
        "header": "Posez des questions médicales pour obtenir des informations. Vous pouvez télécharger des rapports médicaux ou des examens au format PDF pour un diagnostic plus précis.",
        "upload_label": "Ajoutez vos PDFs cliniques",
        "emergency_title": "📞 Numéros d'Urgence",
        "select_country": "Sélectionnez votre pays:",
        "question_placeholder": "🩺 Quelle est votre question médicale ?",
        "response_title": "💡 Réponse de l'IA:",
        "sidebar_title": "📄 Téléchargement de Fichiers (Optionnel)",
        "pdf_success": "✅ PDF '{}' traité avec succès !",
        "pdf_error": "❌ Erreur de lecture du PDF '{}': {}",
        "select_language": "🌐 Langue"
    },
    "Deutsch (Deutschland)": {
        "title": "DiagnosticAI",
        "header": "Stellen Sie medizinische Fragen, um Informationen zu erhalten. Sie können medizinische Berichte oder Untersuchungen im PDF-Format hochladen, um eine genauere Diagnose zu erhalten.",
        "upload_label": "Fügen Sie Ihre klinischen PDFs hinzu",
        "emergency_title": "📞 Notrufnummern",
        "select_country": "Wählen Sie Ihr Land:",
        "question_placeholder": "🩺 Was ist Ihre medizinische Frage?",
        "response_title": "💡 KI-Antwort:",
        "sidebar_title": "📄 Dateiupload (Optional)",
        "pdf_success": "✅ PDF '{}' erfolgreich verarbeitet!",
        "pdf_error": "❌ Fehler beim Lesen der PDF '{}': {}",
        "select_language": "🌐 Sprache"
    },
    "Italiano (Italia)": {
        "title": "DiagnosticAI",
        "header": "Fai domande mediche per ottenere informazioni. Puoi caricare referti medici o esami in PDF per una diagnosi più precisa.",
        "upload_label": "Aggiungi i tuoi PDF clinici",
        "emergency_title": "📞 Numeri di Emergenza",
        "select_country": "Seleziona il tuo paese:",
        "question_placeholder": "🩺 Qual è la tua domanda medica?",
        "response_title": "💡 Risposta dell'IA:",
        "sidebar_title": "📄 Caricamento File (Opzionale)",
        "pdf_success": "✅ PDF '{}' elaborato con successo!",
        "pdf_error": "❌ Errore durante la lettura del PDF '{}': {}",
        "select_language": "🌐 Lingua"
    },
    "日本語 (Japan)": {
        "title": "DiagnosticAI",
        "header": "医療に関する質問をして情報を得ることができます。より正確な診断のために、医療報告書や検査結果をPDFでアップロードできます。",
        "upload_label": "臨床PDFを追加",
        "emergency_title": "📞 緊急連絡先",
        "select_country": "国を選択:",
        "question_placeholder": "🩺 医療に関する質問は何ですか？",
        "response_title": "💡 AIの回答:",
        "sidebar_title": "📄 ファイルアップロード（オプション）",
        "pdf_success": "✅ PDF '{}' の処理に成功しました！",
        "pdf_error": "❌ PDF '{}' の読み込みエラー: {}",
        "select_language": "🌐 言語"
    },
    "English (Australia)": {
        "title": "DiagnosticAI",
        "header": "Ask medical questions to get information. You can upload medical reports or exams in PDF for more accurate diagnosis.",
        "upload_label": "Add your clinical PDFs",
        "emergency_title": "📞 Emergency Numbers",
        "select_country": "Select your country:",
        "question_placeholder": "🩺 What is your medical question?",
        "response_title": "💡 AI Response:",
        "sidebar_title": "📄 File Upload (Optional)",
        "pdf_success": "✅ PDF '{}' processed successfully!",
        "pdf_error": "❌ Error reading PDF '{}': {}",
        "select_language": "🌐 Language"
    },
    "English (Canada)": {
        "title": "DiagnosticAI",
        "header": "Ask medical questions to get information. You can upload medical reports or exams in PDF for more accurate diagnosis.",
        "upload_label": "Add your clinical PDFs",
        "emergency_title": "📞 Emergency Numbers",
        "select_country": "Select your country:",
        "question_placeholder": "🩺 What is your medical question?",
        "response_title": "💡 AI Response:",
        "sidebar_title": "📄 File Upload (Optional)",
        "pdf_success": "✅ PDF '{}' processed successfully!",
        "pdf_error": "❌ Error reading PDF '{}': {}",
        "select_language": "🌐 Language"
    }
}

# Função para extrair texto de PDFs
def extract_text_from_pdfs(uploaded_pdfs, lang):
    text = ""
    for pdf in uploaded_pdfs:
        try:
            with fitz.open(stream=pdf.read(), filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text("text")
            st.success(INTERFACE_TEXTS[lang]["pdf_success"].format(pdf.name))
        except Exception as e:
            st.error(INTERFACE_TEXTS[lang]["pdf_error"].format(pdf.name, str(e)))
    return text

# Função para mostrar números de emergência
def mostrar_numeros_emergencia(lang):
    default_country = COUNTRIES_BY_LANGUAGE.get(lang, "Other")
    emergency_numbers = EMERGENCY_NUMBERS.get(default_country, EMERGENCY_NUMBERS["Other"])
    
    st.sidebar.markdown(f"### {INTERFACE_TEXTS[lang]['emergency_title']}")
    
    # Mostrar os números de emergência do país padrão para o idioma selecionado
    for servico, numero in emergency_numbers.items():
        st.sidebar.markdown(f"**{servico}:** `{numero}`")

# Função para interagir com a IA da Groq para diagnósticos
def diagnosticar_com_groq(pergunta, contexto=None, lang="Português (Brasil)"):
    system_prompt = {
        "Português (Brasil)": """Você é uma inteligência artificial médica especializada em análise preliminar de condições de saúde.""",
        "Português (Portugal)": """Você é uma inteligência artificial médica especializada em análise preliminar de condições de saúde.""",
        "English (United States)": """You are a medical AI specialized in preliminary analysis of health conditions.""",
        "English (United Kingdom)": """You are a medical AI specialized in preliminary analysis of health conditions.""",
        "Español (España)": """Eres una inteligencia artificial médica especializada en el análisis preliminar de condiciones de salud.""",
        "Français (France)": """Vous êtes une intelligence artificielle médicale spécialisée dans l'analyse préliminaire des problèmes de santé.""",
        "Deutsch (Deutschland)": """Sie sind eine medizinische KI, die sich auf die vorläufige Analyse von Gesundheitszuständen spezialisiert hat.""",
        "Italiano (Italia)": """Sei un'IA medica specializzata nell'analisi preliminare delle condizioni di salute.""",
        "日本語 (Japan)": """あなたは健康状態の予備分析を専門とする医療用AIです。""",
        "English (Australia)": """You are a medical AI specialized in preliminary analysis of health conditions.""",
        "English (Canada)": """You are a medical AI specialized in preliminary analysis of health conditions."""
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
    lang = st.sidebar.selectbox(
        INTERFACE_TEXTS["English (United States)"]["select_language"],
        list(INTERFACE_TEXTS.keys()),
        index=0
    )
    
    # Imagem da logo (com largura responsiva)
    st.image(LOGO_PATH, use_container_width=True)

    # Container para o conteúdo principal (acima do input)
    main_container = st.container()

    with st.sidebar:
        st.header(INTERFACE_TEXTS[lang]["sidebar_title"])
        uploaded_pdfs = st.file_uploader(
            INTERFACE_TEXTS[lang]["upload_label"], 
            type="pdf", 
            accept_multiple_files=True
        )
        
        mostrar_numeros_emergencia(lang)

    # Processar PDFs primeiro
    if uploaded_pdfs:
        texto_extraido = extract_text_from_pdfs(uploaded_pdfs, lang)
        st.session_state["texto_clinico"] = texto_extraido

    # Container para o input e resposta na parte inferior
    input_container = st.container()

    with input_container:
        # Adicionar espaço antes do input
        st.write("")  # Espaço vazio
        st.write("")  # Mais espaço
        
        pergunta_usuario = st.text_input(INTERFACE_TEXTS[lang]["question_placeholder"])
        
        if pergunta_usuario:
            contexto = st.session_state.get("texto_clinico", None)
            resposta = diagnosticar_com_groq(pergunta_usuario, contexto, lang)
            
            st.markdown(f"### {INTERFACE_TEXTS[lang]['response_title']}")
            st.markdown(resposta)

    # Conteúdo principal (que ficará acima do input)
    with main_container:
        st.markdown(f"**{INTERFACE_TEXTS[lang]['header']}**")
        # Aqui você pode adicionar outros elementos que devem aparecer acima do input

if __name__ == "__main__":
    main()