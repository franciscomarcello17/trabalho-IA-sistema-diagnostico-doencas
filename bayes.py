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

# Glossário médico (mantido igual ao anterior)
GLOSSARIO = {
    # ... (o mesmo glossário que você já tinha)
}

# Números de emergência por país (atualizado com textos em cada língua)
EMERGENCY_NUMBERS = {
    "🇧🇷 Brasil": {
        "SAMU (Serviço de Atendimento Móvel de Urgência)": "192",
        "Bombeiros": "193", 
        "Polícia Militar": "190",
        "Disque Intoxicação (Anvisa)": "0800-722-6001",
        "Centro de Valorização da Vida (CVV)": "188"
    },
    "🇵🇹 Portugal": {
        "Número Europeu de Emergência": "112",
        "Saúde 24": "808 24 24 24",
        "Centro de Informação Antivenenos": "808 250 143",
        "Polícia de Segurança Pública": "21 342 22 22"
    },
    "🇺🇸 EUA": {
        "Emergency Services": "911",
        "Poison Control Center": "1-800-222-1222",
        "Suicide & Crisis Lifeline": "988",
        "Non-Emergency Police": "311"
    },
    "🇪🇸 Espanha": {
        "Emergencias": "112",
        "Información Toxicológica": "915 620 420",
        "Policía Nacional": "091",
        "Bomberos": "080"
    },
    "🇬🇧 Reino Unido": {
        "Emergency Services": "999",
        "NHS Non-emergency": "111",
        "National Poison Information": "0344 892 0111",
        "Police Non-emergency": "101"
    },
    "🇩🇪 Alemanha": {
        "Notruf": "112",
        "Giftnotruf": "030-19240",
        "Polizei Notruf": "110",
        "Ärztlicher Bereitschaftsdienst": "116 117"
    },
    "🇫🇷 França": {
        "Urgences Médicales (SAMU)": "15",
        "Police Secours": "17",
        "Pompiers": "18",
        "Centre Anti-Poison": "01 40 05 48 48"
    },
    "🇮🇹 Itália": {
        "Emergenza": "112",
        "Emergenza Sanitaria": "118",
        "Centro Antiveleni": "06 4997 7700",
        "Carabinieri": "112"
    },
    "🇯🇵 Japão": {
        "救急車 (Ambulância)": "119",
        "警察 (Polícia)": "110",
        "中毒110番 (Centro de Envenenamento)": "03-3812-7111"
    },
    "🇦🇺 Austrália": {
        "Emergency": "000",
        "Poisons Information": "13 11 26",
        "Police Assistance": "131 444",
        "Suicide Call Back Service": "1300 659 467"
    },
    "🇨🇦 Canadá": {
        "Emergency Services": "911",
        "Poison Control": "1-800-268-9017",
        "Suicide Prevention": "1-833-456-4566",
        "Non-emergency Police": "311"
    },
    "🌍 Outro": {
        "Emergência Internacional": "112 (funciona em muitos países)",
        "Consulte": "o serviço de emergência local"
    }
}

# Função para extrair texto de PDFs (mantida igual)
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

# Função para determinar a cor da triagem (mantida igual)
def determinar_triagem(resposta):
    termos_vermelho = ["emergência", "urgente", "imediatamente", "grave", "risco de vida", 
                      "SAMU", "192", "911", "112", "pronto-socorro", "dor no peito", 
                      "dificuldade respiratória", "sangramento intenso", "perda de consciência",
                      "AVC", "acidente vascular cerebral", "infarto", "convulsão"]
    
    termos_amarelo = ["avaliar", "recomendo consulta", "médico", "exames", "investigar",
                     "possível", "suspeita", "recomendável", "urgência relativa", "monitorar"]
    
    if any(termo.lower() in resposta.lower() for termo in termos_vermelho):
        return "vermelho"
    elif any(termo.lower() in resposta.lower() for termo in termos_amarelo):
        return "amarelo"
    else:
        return "verde"

# Função para adicionar tooltips com glossário (mantida igual)
def adicionar_glossario(texto):
    for termo, definicao in GLOSSARIO.items():
        if termo.lower() in texto.lower():
            texto = texto.replace(termo, f'<span title="{definicao}">{termo}</span>')
    return texto

# Função para interagir com a IA da Groq (mantida igual)
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
    
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages
    )
    return response.choices[0].message.content

# CSS para o botão de emergência e popup
EMERGENCY_CSS = """
<style>
.emergency-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background-color: #ff4b4b;
    color: white;
    border: none;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
}

.emergency-button:hover {
    background-color: #ff0000;
    transform: scale(1.1);
}

.emergency-popup {
    position: fixed;
    bottom: 90px;
    right: 20px;
    width: 350px;
    padding: 20px;
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    z-index: 1001;
    display: none;
}

.emergency-popup.show {
    display: block;
    animation: fadeIn 0.3s;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.emergency-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 15px;
}

.emergency-item {
    padding: 10px;
    background-color: #f8f9fa;
    border-radius: 5px;
    font-size: 14px;
}

.emergency-flag {
    font-size: 24px;
    margin-right: 10px;
}

.country-selector {
    margin-bottom: 15px;
}

.country-option {
    display: inline-block;
    margin: 5px;
    cursor: pointer;
    padding: 5px;
    border-radius: 5px;
}

.country-option:hover {
    background-color: #f0f0f0;
}

.country-option.selected {
    background-color: #e0f7fa;
    border: 1px solid #4dd0e1;
}
</style>
"""

# JavaScript para controlar o popup
EMERGENCY_JS = """
<script>
function toggleEmergencyPopup() {
    const popup = document.querySelector('.emergency-popup');
    popup.classList.toggle('show');
}

function selectCountry(country) {
    document.querySelectorAll('.country-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
    
    document.querySelectorAll('.country-contacts').forEach(contacts => {
        contacts.style.display = 'none';
    });
    document.getElementById(country + '-contacts').style.display = 'block';
}
</script>
"""

# Componente de emergência
def emergency_component():
    st.markdown(EMERGENCY_CSS, unsafe_allow_html=True)
    st.markdown(EMERGENCY_JS, unsafe_allow_html=True)
    
    # Botão flutuante
    st.markdown("""
    <button class="emergency-button" onclick="toggleEmergencyPopup()">🚨</button>
    <div class="emergency-popup">
        <h3 style="margin-top: 0;">Contatos de Emergência</h3>
        <div class="country-selector">
    """, unsafe_allow_html=True)
    
    # Bandeiras/seletores de país
    flags_html = ""
    for i, country in enumerate(EMERGENCY_NUMBERS.keys()):
        flags_html += f"""
        <span class="country-option {'selected' if i==0 else ''}" onclick="selectCountry('country{i}')">
            {country.split()[0]} <span style="font-size:12px">{' '.join(country.split()[1:])}</span>
        </span>
        """
    st.markdown(flags_html, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Contatos por país
    for i, (country, numbers) in enumerate(EMERGENCY_NUMBERS.items()):
        contacts_html = f"""
        <div id="country{i}-contacts" class="country-contacts" style="{'display: block;' if i==0 else 'display: none;'}">
            <div class="emergency-grid">
        """
        for service, number in numbers.items():
            contacts_html += f"""
            <div class="emergency-item">
                <strong>{service}</strong><br>
                <span style="font-size:16px; color: #ff4b4b;">{number}</span>
            </div>
            """
        contacts_html += """
            </div>
        </div>
        """
        st.markdown(contacts_html, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Interface principal
def main():
    # Configuração da página
    st.set_page_config(
        page_title="DiagnosticAI",
        page_icon="⚕️",
        layout="centered"
    )
    
    # Imagem da logo
    st.image(LOGO_PATH, use_column_width=True)

    # CSS para tooltips (mantido igual)
    st.markdown("""
    <style>
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("Faça perguntas médicas para obter informações. Você pode carregar relatórios médicos ou exames em PDF para um diagnóstico mais preciso.")

    # Upload de arquivos
    with st.sidebar:
        st.header("📄 Upload de Arquivos (Opcional)")
        uploaded_pdfs = st.file_uploader("Adicione seus PDFs clínicos", type="pdf", accept_multiple_files=True)

    # Processar PDFs
    if uploaded_pdfs:
        texto_extraido = extract_text_from_pdfs(uploaded_pdfs)
        st.session_state["texto_clinico"] = texto_extraido

    # Campo de pergunta
    pergunta_usuario = st.text_input("🩺 Qual é a sua dúvida médica?")

    # Botão de emergência (sempre visível)
    emergency_component()

    # Processar pergunta
    if pergunta_usuario:
        contexto = st.session_state.get("texto_clinico", None)
        resposta = diagnosticar_com_groq(pergunta_usuario, contexto)
        
        # Determinar nível de urgência
        nivel_triagem = determinar_triagem(resposta)
        
        # Mostrar resposta com formatação de cores
        st.markdown("### ⚠️ Triagem de Urgência")
        if nivel_triagem == "vermelho":
            st.error("🔴 Nível VERMELHO - Procure atendimento médico IMEDIATAMENTE!")
        elif nivel_triagem == "amarelo":
            st.warning("🟡 Nível AMARELO - Recomendada avaliação médica em breve")
        else:
            st.success("🟢 Nível VERDE - Sem urgência aparente")
        
        st.markdown("### 💡 Resposta da IA:")
        
        # Adicionar tooltips do glossário
        resposta_com_glossario = adicionar_glossario(resposta)
        st.markdown(resposta_com_glossario, unsafe_allow_html=True)

if __name__ == "__main__":
    main()