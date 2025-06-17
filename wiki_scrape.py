# wiki_scrape.py
import wikipedia

def get_summary(query, sentences=3):
    """
    Busca o sumário de um tópico da Wikipedia.
    
    Args:
        query (str): O termo a buscar.
        sentences (int): Número de sentenças do resumo.
    
    Returns:
        str: Sumário.
    """
    try:
        summary = wikipedia.summary(query, sentences=sentences, auto_suggest=False)
        return summary
    except Exception as e:
        return f"Erro ao buscar '{query}': {str(e)}"

def get_page_content(query):
    """
    Busca o conteúdo completo de uma página da Wikipedia.
    
    Args:
        query (str): O termo a buscar.
    
    Returns:
        str: Conteúdo completo.
    """
    try:
        page = wikipedia.page(query, auto_suggest=False)
        return page.content
    except Exception as e:
        return f"Erro ao buscar '{query}': {str(e)}"
