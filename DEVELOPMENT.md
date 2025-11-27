# Development Guide

This project uses a modern Python packaging workflow with PDM. The code is organized in `src/`, built as a wheel, installed into a `dist/` folder, and then deployed to Hugging Face Spaces.

## Project Structure

```
hf-chatbot-demo/
├── pyproject.toml           # Project metadata, dependencies, build config
├── pdm.lock                 # Lock file for reproducible installs (commit this)
├── src/
│   └── chatbot/
│       ├── __init__.py
│       ├── app.py           # Main Gradio application
│       ├── rag.py           # RAG (vector store, retrieval)
│       └── rate_limiter.py  # Rate limiting logic
├── scripts/
│   ├── build.py             # Build script: wheel → install → dist/
│   └── upload.py            # Upload script: dist/ → HF Spaces
├── dist/                    # Generated artifact for HF (gitignored)
├── faq.md                   # Your FAQ content
├── README.md                # Main project README
└── DEVELOPMENT.md           # This file
```

## Setup for Development

### 1. Install PDM

```bash
# macOS
brew install pdm

# Linux
curl -sSL https://pdm-project.org/install-pdm.py | python3 -

# Windows
pip install pdm
```

### 2. Install Project Dependencies

```bash
pdm install
```

This installs all dependencies in a virtual environment managed by PDM.

### 3. Run the App Locally (Development Mode)

```bash
pdm run dev
```

This launches the Gradio app at `http://localhost:7860` with hot-reload.

## Building for Production

### Build the Distribution

```bash
pdm run build
```

This does the following:
1. **Builds a wheel** using the standard Python build system
2. **Installs the wheel** into `dist/` using `pip install --target`
3. **Exports requirements.txt** with the exact dependency versions
4. **Creates an entry point** `dist/app.py` that imports and launches the app
5. **Copies supporting files** (`faq.md`, `README.md`) to `dist/`

Result: A clean `dist/` folder ready for Hugging Face.

### Upload to Hugging Face Spaces

First, authenticate with Hugging Face:

```bash
huggingface-cli login
```

Then upload:

```bash
pdm run upload YOUR_USERNAME YOUR_SPACE_NAME
```

Example:
```bash
pdm run upload alice my-store-chatbot
```

This:
1. Creates the Space on HF (if it doesn't exist)
2. Uploads all files from `dist/` to the Space repository
3. HF automatically builds and deploys

## How It Works

### The Build Process (Option B from earlier discussion)

**Step 1: Standard Python Wheel**
```bash
python -m build --wheel
```
Creates a `.whl` file containing the packaged `chatbot` module.

**Step 2: Install to Target Directory**
```bash
pip install dist/*.whl --target dist/
```
Installs the wheel contents into `dist/`, resulting in:
```
dist/
└── chatbot/          # The installed package
    ├── __init__.py
    ├── app.py
    ├── rag.py
    └── rate_limiter.py
```

**Step 3: Generate Requirements**
```bash
# Exports the core dependencies to requirements.txt
```
Hugging Face will use this to install dependencies before running your app.

**Step 4: Create Entry Point**
```python
# dist/app.py
from chatbot.app import demo

if __name__ == "__main__":
    demo.launch()
```
This simple file is what HF runs directly. It imports the installed `chatbot` package.

**Step 5: Copy Supporting Files**
- `faq.md` → Your FAQ content
- `README.md` → Project documentation

### Why This Approach?

✅ **Professional**: Uses standard Python packaging (wheels are the standard distribution format)
✅ **Clean**: `dist/` is a complete, self-contained artifact
✅ **Reproducible**: Lock file (`pdm.lock`) ensures exact same environment every time
✅ **Organized**: Source code stays in `src/`, separate from distribution
✅ **Flexible**: Can easily add more modules or subpackages to `src/chatbot/`
✅ **Maintainable**: All configuration in `pyproject.toml`, no scattered setup files

## Modifying the Code

### Adding a New Module

Create a new file in `src/chatbot/`:

```python
# src/chatbot/models.py
def my_new_function():
    pass
```

Import it in `src/chatbot/app.py`:

```python
from .models import my_new_function
```

When you rebuild, it automatically gets included.

### Updating Dependencies

Edit `pyproject.toml`:

```toml
dependencies = [
    "gradio>=4.0.0",
    "langchain>=0.1.0",
    # Add new dependency here
    "new-package>=1.0.0",
]
```

Then:
```bash
pdm install  # Updates pdm.lock
```

When you build, the new dependency is included in `requirements.txt`.

## Workflow Summary

**Local Development:**
```bash
# Install once
pdm install

# Run app during development
pdm run dev

# Edit code, save, Gradio auto-reloads
```

**Deploy to HF:**
```bash
# Build the distribution artifact
pdm run build

# Upload to HF Space
pdm run upload USERNAME SPACE_NAME
```

That's it! No manual file juggling, no scattered scripts.

## Troubleshooting

### "build" module not found
```bash
pip install build
```

### pdm lock file issues
```bash
rm pdm.lock
pdm install
```

### Port already in use during dev
```bash
pdm run dev  # Gradio will use next available port
```

### Import errors when running dist/app.py locally

The entry point is designed for HF Spaces. For local testing, use `pdm run dev` instead.

## Next Steps

- Replace `faq.md` with your actual FAQ content
- Update the system prompt in `src/chatbot/app.py` if needed
- Modify `pyproject.toml` with your project metadata (author, license, etc.)
- Test locally with `pdm run dev`
- Build and deploy with `pdm run build && pdm run upload USERNAME SPACE_NAME`
