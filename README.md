# 🌿 SABIÁ — Sistema de Assistência Baseado em IA com Arquivos

**SABIÁ** é um sistema RAG (*Retrieval-Augmented Generation*) que integra IA generativa local com arquivos documentais. O projeto permite consultas em linguagem natural sobre documentos PDF armazenados localmente, preservando a privacidade e operando sem dependência de nuvem.

Ideal para pesquisadores, arquivos institucionais e laboratórios de humanidades digitais.

---

## 🔍 Funcionalidades

- 📂 **Indexação de PDFs locais**  
  Carrega e processa arquivos PDF para extração de conteúdo textual.

- 🧠 **Geração de respostas com IA**  
  Utiliza modelos de linguagem baseados em arquitetura LLaMA para responder perguntas de forma contextualizada.

- 📊 **Banco vetorial com FAISS**  
  Armazena embeddings gerados para recuperação semântica eficiente usando FAISS localmente com cache de embeddings.

- 💬 **Interface interativa com Streamlit**  
  Interface web leve e acessível para interação com o sistema.

- 🔒 **Execução 100% local**  
  Todos os dados e modelos são processados localmente, sem enviar nada para a nuvem.

---

## 🧰 Tecnologias utilizadas

- Python 3.11+
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- [FAISS](https://github.com/facebookresearch/faiss)
- [Sentence-Transformers](https://www.sbert.net/)
- Streamlit

---

## ⚙️ Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/usuario/sabia.git
   cd sabia
   ```

2. **Crie e ative um ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o arquivo `.env`**
   Crie um arquivo `.env` com os seguintes parâmetros:
   ```
   MODEL_PATH=models/llm/model.gguf
   DATA_PATH=data/processed
   ```

5. **Adicione seus PDFs em `dataset`**

6. **Inicie a interface**
   ```bash
   streamlit run app.py
   ```

---

## 🚧 Em desenvolvimento

- Suporte a mais formatos além de PDF
- Upload de arquivos via interface
- Cache de perguntas/respostas
- Melhorias de desempenho e otimização de memória

---

## 📜 Licença

Este projeto está licenciado sob a [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html).  
Sinta-se livre para usar, modificar e redistribuir conforme os termos da licença.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para sugerir melhorias, abrir issues ou enviar pull requests, siga as diretrizes no arquivo `CONTRIBUTING.md` (em breve).

---

## ✨ Nome do projeto

**SABIÁ** homenageia o pássaro símbolo do Brasil e reflete a ideia de um assistente que canta conhecimento ao ser provocado — um mensageiro inteligente entre documentos e pessoas.
