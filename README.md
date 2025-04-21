# 🏥 DiagnosticAI - Assistente Médico Inteligente

![Logo](logo.png)  
*Diagnóstico preliminar baseado em IA para análise de exames clínicos*

## 🔍 Visão Geral
O **DiagnosticAI** é uma ferramenta de suporte médico que utiliza inteligência artificial (Groq/Llama3) para:
- Analisar arquivos PDF de exames clínicos
- Responder perguntas médicas com base nos documentos
- Fornecer hipóteses diagnósticas preliminares

⚠️ **Aviso Importante**: Este sistema não substitui diagnóstico médico profissional. Sempre consulte um especialista.

## ✨ Funcionalidades
- **Upload de múltiplos PDFs** (laudos, exames, receitas)
- **Processamento de texto automático** (PyMuPDF)
- **Respostas contextualizadas** pelo modelo Llama-3 70B
- **Interface intuitiva** com Streamlit
- **Tema claro padrão** para melhor legibilidade

## 🛠️ Tecnologias Utilizadas
| Componente       | Tecnologia          |
|------------------|---------------------|
| Framework        | Streamlit           |
| IA               | Groq Cloud (Llama3) |
| PDF Processing   | PyMuPDF (fitz)      |
| Deploy           | Docker/Streamlit Cloud|

## 🚀 Como Usar
1. **Upload de documentos**:
   - Acesse a interface web
   - Adicione seus arquivos PDF na sidebar

2. **Faça sua pergunta**:
   - Ex: "Quais anomalias aparecem neste raio-X?"
   - Ex: "Há indicativos de diabetes nestes exames?"

3. **Receba a análise**:
   - A IA cruzará os dados dos PDFs com seu questionamento
   - Resposta será exibida com observações relevantes

## ⚠️ Limitações
- Não processa PDFs escaneados/imagens (apenas texto)
- Precisão varia conforme qualidade dos documentos
- Sem armazenamento de dados (privacidade garantida)

## 🌐 Demo Online
Acesse nossa versão em produção:  
<a href="https://diagnostico-online.streamlit.app/" target="_blank">
  <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Streamlit App">
</a>
## 📝 Licença
Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.