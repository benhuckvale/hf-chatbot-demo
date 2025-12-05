# HF Chatbot Demo

A RAG-powered customer support chatbot built with Gradio, designed for deployment on Hugging Face Spaces.

## Features

- 🔍 **RAG with FAISS**: Semantic search over FAQ content using HuggingFace embeddings
- 🤖 **Qwen2.5-Coder-32B**: Powered by Qwen via HF Inference API
- 💬 **Conversation Memory**: Remembers last 3 exchanges for context
- ⏱️ **Rate Limiting**: 15 requests/min per IP to prevent abuse
- ⚡ **Streaming Responses**: Real-time response generation
- 🎨 **Gradio 6.x**: Modern chat interface

## Prerequisites

- Python 3.11-3.14
- [PDM](https://pdm-project.org/) for dependency management

## Installation

### 1. Install Dependencies

```bash
pdm install
```

This runs a composite command that:
1. Installs all dependencies from `pyproject.toml` (via `pdm sync --no-self`)
2. Installs PyTorch from the official CPU index (via custom `install-torch` script)

**Why the custom PyTorch setup?** PDM can't handle PyTorch's platform-specific wheels from their custom index. See [PYTORCH_SETUP.md](PYTORCH_SETUP.md) for details.

### 2. Run Development Server

```bash
pdm run dev
```

This launches the Gradio app at http://localhost:7860

## Development Workflow

### Project Structure

```
hf-chatbot-demo/
├── src/chatbot/          # Main application code
│   ├── app.py           # Gradio interface + main logic
│   ├── rag.py           # RAG implementation (embeddings, vector store)
│   └── rate_limiter.py  # IP-based rate limiting
├── scripts/
│   ├── install_torch.py # Custom PyTorch installer
│   ├── build.py         # Build dist/ for HF Spaces
│   └── upload.py        # Upload to HF Spaces
├── faq.md               # FAQ content (customize this!)
├── pyproject.toml       # PDM dependencies and scripts
└── README_SPACE.md      # README for HF Space deployment
```

### Available Commands

```bash
pdm install         # Install all dependencies (including PyTorch)
pdm run dev         # Run development server
pdm run build       # Build distribution for HF Spaces
pdm run upload USER SPACE  # Upload to HF Spaces
```

### Customizing the FAQ

Edit `faq.md` with your own content. The RAG system will:
1. Chunk the content (500 chars with 50 char overlap)
2. Generate embeddings using `sentence-transformers/all-MiniLM-L6-v2`
3. Build a FAISS vector index for similarity search

### Modifying the LLM

In `src/chatbot/app.py`, change the model:

```python
client = InferenceClient("Qwen/Qwen2.5-Coder-32B-Instruct")
```

Other options on HF Inference API:
- `meta-llama/Llama-3.1-8B-Instruct`
- `mistralai/Mistral-7B-Instruct-v0.3`
- `HuggingFaceH4/zephyr-7b-beta`

## Building & Deployment

### Build Distribution

```bash
pdm run build
```

This creates a `dist/` directory containing:
- `chatbot/` - Source code
- `app.py` - Entry point
- `requirements.txt` - Dependencies for HF Spaces
- `faq.md` - FAQ content
- `README.md` - Space documentation (from `README_SPACE.md`)

**Note**: The build only copies source code, not compiled dependencies. HF Spaces will install dependencies from `requirements.txt`.

### Deploy to HuggingFace Spaces

1. Create a Space at https://huggingface.co/new-space
   - SDK: Gradio
   - Hardware: CPU basic (free)

2. Login to HuggingFace:
   ```bash
   huggingface-cli login
   ```
   Use a **write** token.

3. Upload:
   ```bash
   pdm run upload USERNAME SPACE-NAME
   ```

   Example:
   ```bash
   pdm run upload benhuckvale chatbot-demo
   ```

The Space will build automatically. Watch the "Logs" tab for progress.

## PyTorch Installation

This project uses a custom PyTorch installation approach because PDM can't handle PyTorch's platform-specific wheels. See [PYTORCH_SETUP.md](PYTORCH_SETUP.md) for:

- Why the custom approach is needed
- How it works (`resolution.excludes` + custom install script)
- How to customize for CUDA/ROCm

## Security

Git secrets scanning is configured to prevent committing tokens:

```bash
git secrets --scan          # Scan all files
git secrets --scan-history  # Scan commit history
```

Patterns are configured for AWS, HuggingFace, OpenAI, GitHub, GitLab, and Slack tokens.

## Dependencies

### Core
- `gradio>=4.0.0` - Web UI
- `langchain>=0.1.0` - RAG framework
- `sentence-transformers>=2.2.0` - Embeddings (requires PyTorch)
- `faiss-cpu>=1.7.0` - Vector similarity search
- `huggingface-hub>=0.17.0` - HF Inference API

### PyTorch
- `torch>=2.2.0` - Installed separately via custom script
- `numpy<2.0` - Required for torch 2.2.x compatibility

## License

MIT
