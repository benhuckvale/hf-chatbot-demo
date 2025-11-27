"""RAG (Retrieval-Augmented Generation) functionality for the chatbot."""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


def load_and_chunk_faq(file_path: str) -> list[str]:
    """Load FAQ file and split into chunks for RAG.

    Args:
        file_path: Path to FAQ markdown file

    Returns:
        List of text chunks
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. Using sample FAQ.")
        text = """
        ## Shipping
        Q: How long does shipping take?
        A: Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days.

        Q: Do you ship internationally?
        A: Yes, we ship to over 30 countries worldwide. International shipping takes 10-14 business days.

        ## Returns
        Q: What is your return policy?
        A: You can return any item within 30 days of purchase for a full refund. Items must be unused and in original packaging.

        Q: How do I start a return?
        A: Contact our support team at support@example.com with your order number to initiate a return.

        ## Products
        Q: Are your products eco-friendly?
        A: Yes, we use sustainable materials and eco-friendly packaging for all our products.
        """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n## ", "\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(text)
    return chunks


def build_vector_store(chunks: list[str]) -> FAISS:
    """Build FAISS vector store from text chunks.

    Args:
        chunks: List of text chunks

    Returns:
        FAISS vector store
    """
    print("Loading embeddings model...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("Building vector store...")
    vector_store = FAISS.from_texts(chunks, embeddings)
    print("Vector store ready!")

    return vector_store


def retrieve_context(vector_store: FAISS, query: str, k: int = 3) -> str:
    """Retrieve relevant FAQ context for a query.

    Args:
        vector_store: FAISS vector store
        query: User query
        k: Number of relevant documents to retrieve

    Returns:
        Concatenated context from relevant documents
    """
    relevant_docs = vector_store.similarity_search(query, k=k)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    return context
