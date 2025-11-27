# Hugging Face Store Chatbot

A RAG-powered customer support chatbot for ecommerce sites, hosted on Hugging Face Spaces.

## Features

- ✅ RAG (Retrieval-Augmented Generation) using your FAQ content
- ✅ Semantic search with FAISS vector store
- ✅ Rate limiting (15 requests per minute per IP)
- ✅ Conversation memory (remembers last 3 exchanges)
- ✅ Streaming responses for better UX
- ✅ Uses Mistral 7B via Hugging Face Inference API
- ✅ Free hosting on Hugging Face Spaces

## Files Included

- `app.py` - Main Gradio application with RAG implementation
- `requirements.txt` - Python dependencies
- `faq.md` - Sample FAQ content (replace with your own!)
- `README.md` - This file

## Setup Instructions

### Option 1: Web Upload (Easiest)

1. Create a new Space at https://huggingface.co/new-space
   - Name: Choose a name for your chatbot
   - SDK: Select "Gradio"
   - Hardware: Select "CPU basic - Free"
   - Visibility: Public (required for free tier)

2. Click "Files" → "Add file" → "Upload files"
   - Upload all files from this zip

3. Wait for the Space to build (watch the "Logs" tab)

4. Once it says "Running", click the Space URL to test your chatbot!

### Option 2: Git Upload (For Developers)

1. Create a new Space on Hugging Face

2. Clone the Space repository:
   ```bash
   git clone https://huggingface.co/spaces/YOUR-USERNAME/YOUR-SPACE-NAME
   cd YOUR-SPACE-NAME
   ```

3. Copy all files from this zip into the cloned directory

4. Commit and push:
   ```bash
   git add .
   git commit -m "Initial chatbot setup"
   git push
   ```

5. Hugging Face will automatically build and deploy your Space

### Option 3: Hugging Face Hub API (Programmatic)

See the instructions in the "Using the API" section below.

## Customizing Your FAQ

**Important:** Replace the sample `faq.md` with your actual FAQ content!

Tips for good FAQ content:
- Use clear headings (## for sections)
- Write natural Q&A pairs
- Include common customer questions
- Keep answers concise but complete
- Update regularly based on actual customer questions

## Embedding in WordPress

### Simple Iframe Method

Add this HTML to your WordPress page:

```html
<iframe 
    src="https://YOUR-USERNAME-YOUR-SPACE.hf.space" 
    width="100%" 
    height="600px" 
    style="border: none; border-radius: 10px;"
    title="Customer Support Chat">
</iframe>
```

### Floating Chat Button (Advanced)

Create a floating chat button that opens the chatbot:

```html
<style>
  .chat-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: #007bff;
    color: white;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    z-index: 1000;
  }
  .chat-popup {
    position: fixed;
    bottom: 90px;
    right: 20px;
    width: 400px;
    height: 600px;
    display: none;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    z-index: 1000;
  }
  .chat-popup.active {
    display: block;
  }
</style>

<button class="chat-button" onclick="toggleChat()">💬</button>
<iframe id="chat-iframe" class="chat-popup" src="YOUR-SPACE-URL"></iframe>

<script>
function toggleChat() {
  document.getElementById('chat-iframe').classList.toggle('active');
}
</script>
```

## Configuration Options

### Change the LLM Model

In `app.py`, change this line to use a different model:

```python
client = InferenceClient("mistralai/Mistral-7B-Instruct-v0.3")
```

Other good options:
- `meta-llama/Llama-3.1-8B-Instruct` (Llama 3.1)
- `HuggingFaceH4/zephyr-7b-beta` (Zephyr)
- `google/flan-t5-xxl` (Smaller, faster)

### Adjust Rate Limiting

In `app.py`, modify:

```python
MAX_REQUESTS_PER_MINUTE = 15  # Change this number
```

### Change Chunk Size

For longer FAQ answers, increase chunk size:

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Increase to 800-1000 for longer answers
    chunk_overlap=50
)
```

## Troubleshooting

### "Space is sleeping"
Free Spaces sleep after inactivity. First user waits ~30 seconds for wake-up. Upgrade to persistent hardware if needed.

### "Rate limit exceeded" errors
You're hitting Hugging Face Inference API limits. Wait a few minutes or upgrade your HF account.

### Slow responses
This is normal on free CPU hardware. Consider:
- Using a smaller model (flan-t5-large)
- Upgrading to paid GPU Space
- Reducing max_new_tokens in the response

### Chatbot gives wrong answers
- Check your FAQ content is clear and comprehensive
- Adjust chunk_size to better match your content structure
- Increase k value in similarity_search to retrieve more context
- Add more examples to your FAQ

## Cost Breakdown

- **Hugging Face Space (CPU):** FREE
- **Inference API calls:** FREE tier includes rate limits
- **Bandwidth:** FREE (reasonable use)

For high-traffic sites, consider:
- HF Pro ($9/month) for higher rate limits
- Paid Space hardware ($0.60/hour for GPU) for faster responses

## Support

Questions? Issues? 
- Check Hugging Face Spaces documentation
- Visit the Gradio documentation
- Ask in HF community forums

## License

MIT License - Feel free to modify and use for your projects!
