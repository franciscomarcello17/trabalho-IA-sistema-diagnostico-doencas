import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import os
import requests
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import folium_static

# Caminho dinâmico da logo
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(CURRENT_DIR, "logo.png")

# Configurar chave da Groq
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Glossário médico
GLOSSARIO = {
    # Termos gerais
    "hipertensão": "Pressão arterial elevada, geralmente acima de 140/90 mmHg.",
    "diabetes": "Doença metabólica caracterizada por altos níveis de glicose no sangue.",
    "hiperglicemia": "Nível elevado de glicose no sangue (>126 mg/dL em jejum).",
    "hipoglicemia": "Nível baixo de glicose no sangue (<70 mg/dL).",
    
    # Exames e procedimentos
    "ECG": "Eletrocardiograma - exame que registra a atividade elétrica do coração.",
    "EEG": "Eletroencefalograma - exame que avalia a atividade elétrica cerebral.",
    "endoscopia": "Exame que visualiza o trato digestivo alto usando uma câmera.",
    "colonoscopia": "Exame que visualiza o intestino grosso usando uma câmera.",
    
    # Componentes sanguíneos
    "hemoglobina": "Proteína nas hemácias que transporta oxigênio (valores normais: 13-18 g/dL homens, 12-16 g/dL mulheres).",
    "leucócitos": "Células brancas do sangue (valores normais: 4.000-11.000/mm³).",
    "plaquetas": "Fragmentos celulares para coagulação (valores normais: 150.000-450.000/mm³).",
    "hematócrito": "Porcentagem de células vermelhas no sangue (valores normais: 40-54% homens, 36-48% mulheres).",
    
    # Marcadores bioquímicos
    "PCR": "Proteína C-Reativa - marcador de inflamação (normal <5 mg/L).",
    "TSH": "Hormônio estimulante da tireoide (normal 0,4-4,5 mUI/L).",
    "T4 livre": "Tiroxina livre - hormônio tireoidiano (normal 0,8-1,8 ng/dL).",
    "AST/ALT": "Enzimas hepáticas (normal AST <40 U/L, ALT <56 U/L).",
    
    # Função renal
    "creatinina": "Marcador de função renal (normal 0,6-1,3 mg/dL).",
    "ureia": "Produto do metabolismo proteico (normal 15-45 mg/dL).",
    "clearance": "Taxa de filtração glomerular (normal >90 mL/min).",
    
    # Cardiovascular
    "PA": "Pressão arterial (normal <120/80 mmHg).",
    "FC": "Frequência cardíaca (normal 60-100 bpm em repouso).",
    "taquicardia": "Frequência cardíaca >100 bpm.",
    "bradicardia": "Frequência cardíaca <60 bpm.",
    
    # Respiratório
    "FR": "Frequência respiratória (normal 12-20 rpm em adultos).",
    "saturação O2": "Saturação de oxigênio (normal 95-100%).",
    "dispneia": "Dificuldade respiratória.",
    "SpO2": "Saturação periférica de oxigênio medida por oxímetro.",
    
    # Imagem
    "Rx": "Radiografia (raio-X) - exame de imagem por radiação ionizante.",
    "TC": "Tomografia computadorizada - imagens seccionais por raio-X.",
    "RM": "Ressonância magnética - imagens por campo magnético e ondas de rádio.",
    "US": "Ultrassonografia - imagens por ondas ultrassônicas.",
    
    # Medicamentos
    "AAS": "Ácido acetilsalicílico (aspirina) - antiagregante plaquetário.",
    "IBP": "Inibidor de bomba de prótons (omeprazol, pantoprazol).",
    "AINE": "Anti-inflamatório não esteroidal (ibuprofeno, diclofenaco).",
    "betabloqueador": "Classe de medicamentos para hipertensão e arritmias.",
    
    # Especialidades
    "cardiologia": "Especialidade médica que trata do coração e sistema cardiovascular.",
    "neurologia": "Especialidade que trata do sistema nervoso.",
    "ortopedia": "Especialidade que trata do sistema musculoesquelético.",
    "pediatria": "Especialidade médica dedicada a crianças.",
    
    # Emergências
    "AVC": "Acidente Vascular Cerebral - interrupção do fluxo sanguíneo cerebral.",
    "IAM": "Infarto Agudo do Miocárdio (ataque cardíaco).",
    "PCR": "Parada Cardiorrespiratória - cessação da função cardíaca e respiratória.",
    "TEP": "Tromboembolismo Pulmonar - obstrução da artéria pulmonar.",
    
    # Sinais e sintomas
    "cefaleia": "Dor de cabeça.",
    "mialgia": "Dor muscular.",
    "artralgia": "Dor articular.",
    "parestesia": "Formigamento ou dormência.",
    
    # Doenças
    "DPOC": "Doença Pulmonar Obstrutiva Crônica (enfisema e bronquite crônica).",
    "IR": "Insuficiência Renal - perda da função dos rins.",
    "ICC": "Insuficiência Cardíaca Congestiva - incapacidade do coração bombear sangue.",
    "HAS": "Hipertensão Arterial Sistêmica."
}
# Números de emergência por país
EMERGENCY_NUMBERS = {
    "Brasil": {
        "SAMU": "192",
        "Bombeiros": "193", 
        "Polícia Militar": "190",
        "Disque Intoxicação": "0800-722-6001",
        "Centro de Valorização da Vida (CVV)": "188"
    },
    "Portugal": {
        "Emergência": "112",
        "Saúde 24": "808 24 24 24",
        "Intoxicações": "808 250 143"
    },
    "EUA": {
        "Emergência": "911",
        "Poison Control": "1-800-222-1222",
        "Suicide Prevention": "988"
    },
    "Espanha": {
        "Emergência": "112",
        "Toxicologia": "915 620 420"
    },
    "Reino Unido": {
        "Emergência": "999",
        "NHS Direct": "111",
        "Poison Information": "0344 892 0111"
    },
    "Alemanha": {
        "Emergência": "112",
        "Intoxicações": "030-19240"
    },
    "França": {
        "Emergência": "112",
        "SAMU": "15",
        "Centre Anti-Poison": "01 40 05 48 48"
    },
    "Itália": {
        "Emergência": "112",
        "Emergência Médica": "118",
        "Centro Antiveleni": "06 4997 7700"
    },
    "Japão": {
        "Emergência": "119",
        "Polícia": "110"
    },
    "Austrália": {
        "Emergência": "000",
        "Poisons Information": "13 11 26"
    },
    "Canadá": {
        "Emergência": "911",
        "Poison Control": "1-800-268-9017"
    },
    "Outro": {
        "Consulte": "o serviço de emergência local",
        "Emergência Internacional": "112 (funciona em muitos países)"
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

# Função para determinar a cor da triagem
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

# Função para mostrar números de emergência
def mostrar_numeros_emergencia():
    st.sidebar.markdown("### 📞 Números de Emergência")
    pais_selecionado = st.sidebar.selectbox("Selecione seu país:", list(EMERGENCY_NUMBERS.keys()))
    
    for servico, numero in EMERGENCY_NUMBERS[pais_selecionado].items():
        st.sidebar.markdown(f"**{servico}:** `{numero}`")

# Função para criar mapa de hospitais próximos
def criar_mapa_hospitais(localizacao_usuario):
    try:
        geolocator = Nominatim(user_agent="diagnostic_ai")
        location = geolocator.geocode(localizacao_usuario)
        
        if location:
            mapa = folium.Map(location=[location.latitude, location.longitude], zoom_start=13)
            
            # Adicionar marcador do usuário
            folium.Marker(
                [location.latitude, location.longitude],
                popup="Sua localização",
                icon=folium.Icon(color="blue")
            ).add_to(mapa)
            
            # Buscar hospitais próximos (usando Nominatim - para produção, considere API especializada)
            hospitais = geolocator.geocode("hospital", exactly_one=False, limit=5, 
                                          viewbox=[[location.latitude-0.1, location.longitude-0.1], 
                                                  [location.latitude+0.1, location.longitude+0.1]])
            
            if hospitais:
                for hospital in hospitais:
                    folium.Marker(
                        [hospital.latitude, hospital.longitude],
                        popup=hospital.address,
                        icon=folium.Icon(color="red", icon="plus-sign")
                    ).add_to(mapa)
            
            return mapa
        else:
            st.warning("Não foi possível determinar sua localização. Verifique o endereço.")
            return None
    except Exception as e:
        st.error(f"Erro ao criar mapa: {e}")
        return None

# Função para adicionar tooltips com glossário
def adicionar_glossario(texto):
    for termo, definicao in GLOSSARIO.items():
        if termo.lower() in texto.lower():
            texto = texto.replace(termo, f'<span title="{definicao}">{termo}</span>')
    return texto

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
    
    # Imagem da logo (com largura responsiva)
    st.image(LOGO_PATH, use_container_width=True)

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

    with st.sidebar:
        st.header("📄 Upload de Arquivos (Opcional)")
        uploaded_pdfs = st.file_uploader("Adicione seus PDFs clínicos", type="pdf", accept_multiple_files=True)
        
        mostrar_numeros_emergencia()
        
        st.header("🏥 Localização para Hospitais")
        localizacao_usuario = st.text_input("Digite seu endereço ou cidade para encontrar hospitais próximos:")
        if localizacao_usuario:
            mapa = criar_mapa_hospitais(localizacao_usuario)
            if mapa:
                folium_static(mapa)

    if uploaded_pdfs:
        texto_extraido = extract_text_from_pdfs(uploaded_pdfs)
        st.session_state["texto_clinico"] = texto_extraido

    pergunta_usuario = st.text_input("🩺 Qual é a sua dúvida médica?")

    if pergunta_usuario:
        contexto = st.session_state.get("texto_clinico", None)
        resposta = diagnosticar_com_groq(pergunta_usuario, contexto)
        
        # Determinar nível de urgência
        nivel_triagem = determinar_triagem(resposta)
        
        # Mostrar resposta com formatação de cores
        st.markdown("### � Triagem de Urgência")
        if nivel_triagem == "vermelho":
            st.error("🔴 Nível VERMELHO - Procure atendimento médico IMEDIATAMENTE!")
        elif nivel_triagem == "amarelo":
            st.warning("🟡 Nível AMARELO - Recomendada avaliação médica em breve")
        else:
            st.success("🟢 Nível VERDE - Sem urgência aparente")
        
        st.markdown("### � Resposta da IA:")
        
        # Adicionar tooltips do glossário
        resposta_com_glossario = adicionar_glossario(resposta)
        st.markdown(resposta_com_glossario, unsafe_allow_html=True)
        
        # Mostrar mapa novamente se for caso de emergência
        if nivel_triagem in ["vermelho", "amarelo"]:
            st.markdown("### 🏥 Hospitais Próximos")
            if 'localizacao_usuario' in locals() and localizacao_usuario:
                mapa = criar_mapa_hospitais(localizacao_usuario)
                if mapa:
                    folium_static(mapa)
            else:
                st.warning("Digite sua localização na barra lateral para visualizar hospitais próximos.")

if __name__ == "__main__":
    main()