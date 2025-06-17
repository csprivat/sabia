
import os
import fitz  # PyMuPDF

def extract_text_from_pdf(file_path):
    """Extrai texto de todas as páginas de um PDF e retorna como um único texto."""
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

def chunk_text(text, words_per_chunk=500):
    """Divide um texto longo em blocos com número fixo de palavras."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), words_per_chunk):
        chunk = " ".join(words[i:i + words_per_chunk])
        chunks.append(chunk)
    return chunks

def load_pdf_chunks(pdf_folder="data/pdfs/", words_per_chunk=500):
    """
    Lê todos os PDFs da pasta especificada, divide o texto em blocos e retorna uma lista de dicionários.

    Cada dicionário tem:
        - 'source': nome do arquivo PDF
        - 'chunk_id': índice do bloco
        - 'text': conteúdo do bloco
    """
    dataset = []
    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(pdf_folder, filename)
            try:
                full_text = extract_text_from_pdf(file_path)
                chunks = chunk_text(full_text, words_per_chunk)
                for i, chunk in enumerate(chunks):
                    dataset.append({
                        "source": filename,
                        "chunk_id": i,
                        "text": chunk
                    })
            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")
    return dataset
