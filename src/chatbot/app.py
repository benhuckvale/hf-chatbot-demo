"""Main Gradio app for the RAG-powered chatbot."""

import os
import gradio as gr
from huggingface_hub import InferenceClient

from .rag import load_and_chunk_faq, build_vector_store, retrieve_context
from .rate_limiter import check_rate_limit


# Initialize models
print("Initializing RAG system...")
chunks = load_and_chunk_faq("faq.md")
print(f"Created {len(chunks)} chunks from FAQ")
vector_store = build_vector_store(chunks)

# Initialize the LLM client (using Mistral via Inference API)
# Mistral-7B-Instruct-v0.2 is routed through Featherless AI inference provider
# Requires HF_API_TOKEN in HF Spaces, works in local dev + CI with HF token
hf_token = (
    os.getenv("HF_API_TOKEN")      # HF Spaces
    or os.getenv("HF_HUB_TOKEN")   # Newer alias
    or os.getenv("HF_TOKEN")       # Local: huggingface-cli login
)

client = InferenceClient(
    "mistralai/Mistral-7B-Instruct-v0.2",
    token=hf_token
)

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
            for exchange in history[-3:]:  # Last 3 exchanges
                if isinstance(exchange, (list, tuple)) and len(exchange) >= 2:
                    human, assistant = exchange[0], exchange[1]
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

        # Build messages for chat completion
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        # Generate response using chat completion API
        response = ""
        for message_chunk in client.chat_completion(
            messages=messages,
            max_tokens=300,
            temperature=0.7,
            stream=True,
        ):
            if hasattr(message_chunk, 'choices') and len(message_chunk.choices) > 0:
                delta = message_chunk.choices[0].delta
                if hasattr(delta, 'content') and delta.content:
                    response += delta.content
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
    ]
)

# Apply theme to the demo
demo.theme = gr.themes.Soft()


if __name__ == "__main__":
    demo.launch(share=False)
