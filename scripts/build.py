"""Build script to create distribution artifact for Hugging Face Spaces."""

import shutil
import sys
from pathlib import Path


def main():
    """Build the distribution package for HF Spaces."""
    repo_root = Path(__file__).parent.parent
    dist_dir = repo_root / "dist"

    print("=" * 60)
    print("Building distribution for Hugging Face Spaces")
    print("=" * 60)

    # Clean previous dist
    if dist_dir.exists():
        print(f"\n🗑️  Cleaning previous dist directory...")
        shutil.rmtree(dist_dir)

    # Create dist directory
    print(f"\n📂 Creating dist directory...")
    dist_dir.mkdir()
    print(f"✅ Created dist/")

    # Copy source code
    print(f"\n📦 Copying source code...")
    src_dir = repo_root / "src" / "chatbot"
    dest_chatbot = dist_dir / "chatbot"

    if not src_dir.exists():
        print(f"❌ Source directory not found: {src_dir}")
        return False

    # Copy directory, excluding __pycache__ and .pyc files
    shutil.copytree(
        src_dir,
        dest_chatbot,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
    )
    print(f"✅ Copied chatbot/ package")

    # Create requirements.txt
    print(f"\n📋 Creating requirements.txt...")
    requirements = [
        "torch>=2.0.0",  # HF Spaces will install from PyPI
        "numpy<2.0",     # Compatibility with torch 2.2.x
        "gradio>=4.0.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-text-splitters>=0.0.1",
        "langchain-huggingface>=0.0.1",
        "sentence-transformers>=2.2.0",
        "faiss-cpu>=1.7.0",
        "huggingface-hub>=0.17.0",
    ]

    requirements_file = dist_dir / "requirements.txt"
    with open(requirements_file, "w") as f:
        f.write("\n".join(requirements) + "\n")
    print(f"✅ requirements.txt")

    # Create entry point app.py
    print(f"\n🚀 Creating app.py entry point...")
    app_py = dist_dir / "app.py"
    app_py.write_text(
        """\"\"\"Entry point for Hugging Face Spaces.\"\"\"

from chatbot.app import demo

if __name__ == "__main__":
    demo.launch()
"""
    )
    print(f"✅ app.py")

    # Copy supporting files
    print(f"\n📄 Copying data files...")

    # Copy faq.md
    faq_src = repo_root / "faq.md"
    if faq_src.exists():
        shutil.copy(faq_src, dist_dir / "faq.md")
        print(f"   ✅ faq.md")
    else:
        print(f"   ⚠️  faq.md not found")

    # Copy README_SPACE.md as README.md for HF Space
    readme_src = repo_root / "README_SPACE.md"
    if readme_src.exists():
        shutil.copy(readme_src, dist_dir / "README.md")
        print(f"   ✅ README.md (from README_SPACE.md)")
    else:
        print(f"   ⚠️  README_SPACE.md not found")

    print(f"\n" + "=" * 60)
    print(f"✅ Distribution ready in: dist/")
    print(f"=" * 60)
    print(f"\nContents:")
    for item in sorted(dist_dir.iterdir()):
        if item.is_file():
            size = item.stat().st_size
            print(f"  {item.name} ({size} bytes)")
        else:
            print(f"  {item.name}/ (directory)")

    print(f"\nNext: Run 'pdm run upload' to deploy to Hugging Face Spaces")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
