from langchain.embeddings import OpenAIEmbeddings


def get_embeddings():
    return OpenAIEmbeddings(chunk_size=200)
