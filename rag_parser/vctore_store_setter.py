import os
from dotenv import load_dotenv

load_dotenv()
from pathlib import Path
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader
from pinecone import Pinecone, ServerlessSpec

INDEX_NAME = os.getenv("INDEX_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
DIMENSION = int(os.getenv("VECTOR_DB_DIMENSION"))
METRIC = os.getenv("VECTOR_DB_METRIC")
CLOUD = os.getenv("VECTOR_DB_CLOUD")
REGION = os.getenv("VECTOR_DB_REGION")
requirement_file_path = Path(__file__).parent.parent / "requirements.docx"
embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)


def intialize_and_ingest_pinecode():
    pc = Pinecone()
    existing_indexes = [index.name for index in pc.list_indexes()]
    if INDEX_NAME not in existing_indexes:
        {
            pc.create_index(
                name=INDEX_NAME,
                dimension=DIMENSION,
                metric=METRIC,
                spec=ServerlessSpec(cloud=CLOUD, region=REGION),
            )
        }
    print("requirement file path: ", requirement_file_path)    
    DOCX_LOADER = Docx2txtLoader(requirement_file_path)
    documents = DOCX_LOADER.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    vector_store = PineconeVectorStore.from_documents(
        texts, embeddings, index_name=INDEX_NAME
    )
    return vector_store


def retrieve_context(query: str, k: int = 5):
    vector_store = PineconeVectorStore.from_existing_index(
        index_name=INDEX_NAME, embedding=embeddings
    )
    docs = vector_store.similarity_search(query, k=k)
    return "\n---\n".join([doc.page_content for doc in docs])
