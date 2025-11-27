import gradio as gr
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from huggingface_hub import InferenceClient
import time
from collections import defaultdict
from datetime import datetime, timedelta

# Simple rate limiting
request_history = defaultdict(list)
MAX_REQUESTS_PER_MINUTE = 15

def check_rate_limit(ip_address):
    """Simple rate limiter: 15 requests per minute per IP"""
    now = datetime.now()
    cutoff = now - timedelta(minutes=1)
    
    # Remove old requests
    request_history[ip_address] = [
        req_time for req_time in request_history[ip_address] 
        if req_time > cutoff
    ]
    
    # Check limit
    if len(request_history[ip_address]) >= MAX_REQUESTS_PER_MINUTE:
        return False
    
    # Add this request
    request_history[ip_address].append(now)
    return True

# Load and chunk your FAQ document
def load_and_chunk_faq(file_path):
    """Load FAQ file and split into chunks for RAG"""
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

print("Loading embeddings model...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print("Loading and chunking FAQ document...")
chunks = load_and_chunk_faq("faq.md")
print(f"Created {len(chunks)} chunks from FAQ")

print("Building vector store...")
vector_store = FAISS.from_texts(chunks, embeddings)
print("Vector store ready!")

# Initialize the LLM client (using Mistral 7B via Inference API)
client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.3")

def respond(message, history, request: gr.Request):
    """Main chatbot response function with RAG"""
    
    # Get client IP for rate limiting
    client_ip = request.client.host if request else "unknown"
    
    # Check rate limit
    if not check_rate_limit(client_ip):
        return "You're sending too many messages. Please wait a minute and try again."
    
    if not message.strip():
        return "Please ask me a question!"
    
    try:
        # Find relevant FAQ chunks using semantic search
        relevant_docs = vector_store.similarity_search(message, k=3)
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        # Build conversation history for context
        conversation_context = ""
        if history:
            for human, assistant in history[-3:]:  # Last 3 exchanges
                conversation_context += f"User: {human}\nAssistant: {assistant}\n\n"
        
        # Build the system prompt with FAQ context
        system_prompt = f"""You are a helpful customer support assistant for an online store. 
Answer questions based on the FAQ content provided below. 

IMPORTANT GUIDELINES:
- Be friendly, helpful, and concise
- If the answer is in the FAQ, provide it clearly
- If the answer ISN'T in the FAQ, politely say you don't have that specific information and suggest contacting support
- Don't make up information that's not in the FAQ
- Keep responses under 150 words

FAQ Content:
{context}

Previous conversation:
{conversation_context}"""
        
        # Format prompt for Mistral model
        prompt = f"<s>[INST] {system_prompt}\n\nCurrent question: {message} [/INST]"
        
        # Generate response using Inference API
        response = ""
        for token in client.text_generation(
            prompt,
            max_new_tokens=300,
            temperature=0.7,
            stream=True,
            details=True
        ):
            if hasattr(token, 'token'):
                response += token.token.text
                yield response
            else:
                response += str(token)
                yield response
                
    except Exception as e:
        yield f"Sorry, I encountered an error. Please try again. (Error: {str(e)})"

# Create the Gradio ChatInterface
demo = gr.ChatInterface(
    respond,
    title="🛍️ Store Support Chat",
    description="Ask me anything about shipping, returns, products, or policies!",
    examples=[
        "How long does shipping take?",
        "What's your return policy?",
        "Do you ship internationally?",
        "Are your products eco-friendly?"
    ],
    theme=gr.themes.Soft(),
    retry_btn=None,
    undo_btn=None,
    clear_btn="Clear Chat"
)

if __name__ == "__main__":
    demo.launch(share=False)
