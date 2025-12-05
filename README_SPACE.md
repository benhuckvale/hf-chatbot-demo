---
title: Store Support Chatbot
emoji: 🛍️
colorFrom: blue
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
---

# Store Support Chatbot

A RAG-powered customer support chatbot using Qwen2.5-Coder-32B-Instruct via Hugging Face Inference API.

## Features

- 🔍 RAG (Retrieval-Augmented Generation) with FAISS vector search
- 💬 Conversation memory (last 3 exchanges)
- ⏱️ Rate limiting (15 requests/min per IP)
- 🎯 Semantic search over FAQ content
- ⚡ Streaming responses

## Customizing Your FAQ

Replace `faq.md` with your own FAQ content! Use clear headings, natural Q&A pairs, and keep answers concise.

## Embedding in Your Website

Simple iframe:
```html
<iframe
    src="https://YOUR-USERNAME-YOUR-SPACE.hf.space"
    width="100%"
    height="600px"
    style="border: none;"
    title="Customer Support Chat">
</iframe>
```

## Development

For development setup, configuration options, and deployment instructions, see the [source repository](https://github.com/YOUR-USERNAME/hf-chatbot-demo).

## License

MIT License
