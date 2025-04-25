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
        "select_language": "🌐 Idioma",
        "warning_title": "⚠️ Aviso Importante",
        "warning_message": "As informações fornecidas por esta IA são preliminares e podem conter imprecisões. Sempre consulte um profissional de saúde para diagnóstico e tratamento. Em emergências, procure atendimento médico imediatamente.",
        "references_title": "📚 Fontes e Referências",
        "references_text": "As informações foram compiladas a partir de fontes médicas confiáveis, incluindo diretrizes clínicas atualizadas e literatura médica reconhecida. Consulte sempre um profissional para orientação específica."
    },
    # ... (os outros idiomas permanecem com a mesma estrutura, adicione as novas chaves para cada um)
    # Adicione as mesmas novas chaves para todos os outros idiomas
}

# Adicione as traduções para os novos textos em todos os idiomas
for lang in INTERFACE_TEXTS:
    if lang != "Português (Brasil)":
        INTERFACE_TEXTS[lang].update({
            "warning_title": "⚠️ Important Warning",
            "warning_message": "The information provided by this AI is preliminary and may contain inaccuracies. Always consult a healthcare professional for diagnosis and treatment. In emergencies, seek immediate medical attention.",
            "references_title": "📚 Sources and References",
            "references_text": "Information was compiled from reliable medical sources, including updated clinical guidelines and recognized medical literature. Always consult a professional for specific guidance."
        })

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
        # ... (outros idiomas permanecem iguais)
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
            7. Incluir ao final da resposta uma seção com as principais fontes médicas utilizadas
            
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
    
    # Inicializar estado da sessão para controlar o aviso
    if "first_question_asked" not in st.session_state:
        st.session_state.first_question_asked = False
    
    # Seleção de idioma
    lang = st.sidebar.selectbox(
        INTERFACE_TEXTS["English (United States)"]["select_language"],
        list(INTERFACE_TEXTS.keys()),
        index=0
    )
    
    # Imagem da logo (com largura responsiva)
    st.image(LOGO_PATH, use_column_width=True)

    st.markdown(f"**{INTERFACE_TEXTS[lang]['header']}**")

    # Mostrar aviso apenas se for a primeira vez
    if not st.session_state.first_question_asked:
        with st.container():
            st.warning(f"""
            **{INTERFACE_TEXTS[lang]['warning_title']}**  
            {INTERFACE_TEXTS[lang]['warning_message']}
            """)

    with st.sidebar:
        st.header(INTERFACE_TEXTS[lang]["sidebar_title"])
        uploaded_pdfs = st.file_uploader(
            INTERFACE_TEXTS[lang]["upload_label"], 
            type="pdf", 
            accept_multiple_files=True
        )
        
        mostrar_numeros_emergencia(lang)

    if uploaded_pdfs:
        texto_extraido = extract_text_from_pdfs(uploaded_pdfs, lang)
        st.session_state["texto_clinico"] = texto_extraido

    pergunta_usuario = st.text_input(INTERFACE_TEXTS[lang]["question_placeholder"])

    if pergunta_usuario:
        # Marcar que a primeira pergunta foi feita
        st.session_state.first_question_asked = True
        
        contexto = st.session_state.get("texto_clinico", None)
        resposta = diagnosticar_com_groq(pergunta_usuario, contexto, lang)
        
        st.markdown(f"### {INTERFACE_TEXTS[lang]['response_title']}")
        st.markdown(resposta)
        
        # Adicionar seção de referências formatada
        with st.expander(INTERFACE_TEXTS[lang]["references_title"]):
            st.markdown(f"""
            <div style="
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 15px;
                border-left: 4px solid #4e73df;
                margin-top: 20px;
            ">
                <p style="margin-bottom: 0;">{INTERFACE_TEXTS[lang]['references_text']}</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()