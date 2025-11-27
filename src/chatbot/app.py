"""Main Gradio app for the RAG-powered chatbot."""

import gradio as gr
from huggingface_hub import InferenceClient

from .rag import load_and_chunk_faq, build_vector_store, retrieve_context
from .rate_limiter import check_rate_limit


# Initialize models
print("Initializing RAG system...")
chunks = load_and_chunk_faq("faq.md")
print(f"Created {len(chunks)} chunks from FAQ")
vector_store = build_vector_store(chunks)

# Initialize the LLM client (using Mistral 7B via Inference API)
client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.3")


def respond(message: str, history: list, request: gr.Request) -> str:
    """Main chatbot response function with RAG.

    Args:
        message: User message
        history: Chat history
        request: Gradio request object for IP extraction

    Yields:
        Streamed response text
    """
    # Get client IP for rate limiting
    client_ip = request.client.host if request else "unknown"

    # Check rate limit
    if not check_rate_limit(client_ip):
        yield "You're sending too many messages. Please wait a minute and try again."
        return

    if not message.strip():
        yield "Please ask me a question!"
        return

    try:
        # Retrieve relevant FAQ context
        context = retrieve_context(vector_store, message, k=3)

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
