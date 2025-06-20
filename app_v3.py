import os
import streamlit as st
import RAG_chain as rc
import wiki_scrape as ws
import re

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.llms import Ollama
from langchain_core.messages import AIMessage, HumanMessage
import ollama

chunk_type = "Recursive"
chunk_size = 800
chunk_overlap = 100

SESSION_ID = "1234"
B_INST, E_INST = "<s>[INST]", "[/INST]</s>"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"


def create_context_aware_chain(retriever, model_name, temperature, num_predict):
    """
    Create a context aware chain with an appropriate system prompt. the temperature of the model is 0.
    """
    llm_summarise = Ollama(model=model_name, temperature=temperature, num_predict=num_predict)

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is.")

    hist_aware_retr = rc.create_rephrase_history_chain(llm_summarise, retriever, contextualize_q_system_prompt)

    return hist_aware_retr


def create_answering_chain(model_name, retriever, temperature, num_predict, system_prompt):
    llm_answer = Ollama(model=model_name, temperature=temperature, num_predict=num_predict)

    system_prompt = system_prompt

    # here we increase the temperature since we want the model to have some creativity in generating the answer without reporting exactly what's written in the context
    full_rag_chain_with_history = rc.create_qa_RAG_chain_history(llm_answer, retriever, system_prompt)

    return full_rag_chain_with_history


def chunk_docs(docs):
    """
    Chunks the documents with a HTMLSplitter and then a RecursiveCharacterSplitter
    :param docs: documents to split
    :return: chunked documents
    """
    headers_to_split_on = [("h1", "Header 1"), ("h2", "Header 2"), ("h3", "Header 3"), ("h4", "Header 4")]
    params = {}

    match chunk_type:
        case "Recursive":
            separators = ["\n\n", "\n", "(?<=\. )", " ", ""]
            params["separators"] = separators
            params["chunk_size"] = chunk_size
            params["chunk_overlap"] = chunk_overlap

            chunks = rc.chunk(docs, headers_to_split_on, chunk_type, **params)

    print("Number of chunks: ", len(chunks))
    print("Number of documents: ", len(docs))

    return chunks



from langchain_core.documents import Document
from pdf_loader import load_pdf_chunks

def create_retriever(directory):
    """Creates a vector index from the PDF files in a directory and returns the retriever associated with it."""
    print("Importing PDF Documents...")
    chunks = load_pdf_chunks(directory)

    print("Converting to LangChain Documents...")
    docs = [
        Document(page_content=chunk["text"], metadata={"source": chunk["source"], "chunk_id": chunk["chunk_id"]})
        for chunk in chunks if chunk["text"].strip()
    ]

    print("Creating a vector store")
    embedding_model, vector_index = rc.create_vector_index_and_embedding_model(docs)

    print("Generating retriever")
    retriever = vector_index.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    return retriever


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Returns a ChatMessageHistory object for the given session_id with the messages between user and AI in the current session.
    The object stores the full history of the conversation.
    :param session_id:
    :return:
    """
    if session_id not in st.session_state.chat_store:
        st.session_state.chat_store[session_id] = ChatMessageHistory()
    return st.session_state.chat_store[session_id]


def get_response(full_chain, session_id, user_query):
    """
    Prompts the llm and returns the answer to the user_query using a full chain considering the history as well.
    """
    answer = full_chain.invoke({"input": user_query}, config={
        "configurable": {"session_id": session_id}
    })

    return answer["answer"]

def folder_added():
    """
    Function called when the user sets the folder in the interface. It generates a vector store.
    Sets the retriever in a session_state veriable to make it persistent
    """
    with st.spinner("Creating vector retriever, please wait..."):
        st.session_state.disabled_sum_model = False
        st.session_state.retriever = create_retriever(st.session_state.files_folder)

def update_summarization_model():
    st.session_state.disabled_ans_model = False
    model_name = st.session_state.sum_model

    ollama_model_name = re.search("(.*)  Size:", model_name).group(1)
    st.session_state.retriever_chain = create_context_aware_chain(st.session_state.retriever, ollama_model_name, st.session_state.temperature, st.session_state.num_predict)

def update_answer_model():
    model_name = st.session_state.ans_model
    ollama_model_name = re.search("(.*)  Size:", model_name).group(1)

    st.session_state.retriever_answer_chain = create_answering_chain(ollama_model_name, st.session_state.retriever_chain, st.session_state.temperature, st.session_state.num_predict, st.session_state.custom_prompt)

    st.session_state.final_chain = RunnableWithMessageHistory(
        st.session_state.retriever_answer_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )


st.set_page_config(page_title="SabIÁ", page_icon="🦜")
st.subheader("Eu sou :blue[SABIÁ] - Como posso te ajudar? 🐦")

# Initially, the dropdown menus for the answering and summarizarion model are disabled.
if "disabled_ans_model" not in st.session_state:
    st.session_state.disabled_ans_model = True

if "disabled_sum_model" not in st.session_state:
    st.session_state.disabled_sum_model = True
st.caption("---   ")

# Instantiates a sidebar
with st.sidebar:
    # Returns the list of ollama models available in ollama on the device
    models_ollama = ollama.list()["models"]
    # extract name and size of the model (in GB)
    model_name = [m['name'] for m in models_ollama]
    model_size = [float(m["size"]) for m in models_ollama]
    name_detail = zip(model_name, model_size)
    # Sort the models based on their size, in ascending order. Faster (smaller models) first
    name_detail = sorted(name_detail, key=lambda x: x[1])
    model_info = [f"{name}  Size: {size/(10**9):.2f}GB" for name, size in name_detail]
    st.text_input("Insira o nome do diretório que contém os arquivos .PDF que serão usados pelo RAG", on_change=folder_added, key="files_folder")
    st.selectbox("Choose a model for context summarization", model_info, index=None, on_change=update_summarization_model, placeholder="Select model", key="sum_model", disabled=st.session_state.disabled_sum_model)
    st.selectbox("Choose a model for answering", model_info, index=None, on_change=update_answer_model, placeholder="Select model", key="ans_model", disabled=st.session_state.disabled_ans_model)

    st.text_area(
        "Prompt do Sistema (customizável)",
        key="custom_prompt",
        height=200,
        value="""You are a senior expert in public procurement in Brazil, with deep knowledge of applicable legislation, case law, legal doctrine, and administrative practices. Your expertise includes legal, technical, and documentary analysis of bidding processes, with the ability to identify risks, irregularities, excessive requirements, formalization errors, and inconsistencies in the notice and its annexes. Based on the information provided, deliver a clear, objective, and well-founded assessment. If the data is insufficient for a reliable analysis, explicitly indicate this limitation. Keep your response concise and accurate. Respond in Brazilian Portuguese.

   ADDITIONAL INFORMATION: {context}""",
        help="Você pode editar esse prompt para guiar o comportamento do modelo de resposta."
    )


    st.caption("---   ")
    st.session_state.temperature = st.slider(
        "Temperatura do modelo",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
        help="Controla a aleatoriedade das respostas. 0.0 = determinístico, 1.0 = mais criativo"
    )

    st.session_state.num_predict = st.slider(
        "Janela de contexto (número de tokens gerados)",
        min_value=64,
        max_value=1024,
        value=256,
        step=64,
        help="Define quantos tokens o modelo pode gerar na resposta"
    )

    st.caption("---   ")
    st.caption("CopyLeft 2025 - Cristian Privat -  https://github.com/csprivat/")
    st.caption("\n⚠️ Lembre-se: Modelos fortemente quantizados terão um desempenho ligeiramente inferior, mas serão muito mais rápidos")


if "disabled" not in st.session_state:
    st.session_state.disabled = False

if "chat_store" not in st.session_state:
    st.session_state.chat_store = {}
def disable():
    st.session_state.disabled = True
def enable():
    st.session_state.disabled = False

# Create the history
if SESSION_ID not in st.session_state.chat_store:
    st.session_state.chat_store[SESSION_ID] = ChatMessageHistory()

# prints the chat history going through the chat_store
for message in st.session_state.chat_store[SESSION_ID].messages:
    MESSAGE_TYPE = "AI" if isinstance(message, AIMessage) else "Human"
    if isinstance(message, AIMessage):
        prefix = "AI"
    else:
        prefix = "Human"

    with st.chat_message(MESSAGE_TYPE):
        st.write(message.content)

if user_query := st.chat_input("Type your message ✍", disabled=st.session_state.disabled, on_submit=disable):
    # Returns an error if any of the fields on the left is unfilled
    if "retriever" not in st.session_state:
        st.error("Retriever, summarization model and answering model were not set.")
    elif "retriever_chain" not in st.session_state:
        st.error("Summarization model and answering model were not set.")
    elif "retriever_answer_chain" not in st.session_state:
        st.error("Answering model was not set.")
    # If all is good, then a spinner will be shown on screen telling the answer in being generated and the chat input will be disabled until the generation is done.
    elif user_query is not None and user_query != "":
        with st.spinner("The model is generating an answer, please wait"):
            response = get_response(st.session_state.final_chain, SESSION_ID, user_query)
            st.session_state.disabled = False
            st.rerun()