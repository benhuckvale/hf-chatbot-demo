"""Build script to create distribution artifact for Hugging Face Spaces."""

import subprocess
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

    # Build wheel
    print(f"\n📦 Building wheel...")
    result = subprocess.run(
        [sys.executable, "-m", "build", "--wheel"],
        cwd=repo_root,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ Build failed:")
        print(result.stderr)
        return False

    print(f"✅ Wheel built successfully")

    # Find the wheel file
    wheel_dir = repo_root / "dist"
    wheel_files = list(wheel_dir.glob("*.whl"))

    if not wheel_files:
        print(f"❌ No wheel file found in {wheel_dir}")
        return False

    wheel_file = wheel_files[0]
    print(f"   Found: {wheel_file.name}")

    # Create clean dist directory for HF
    print(f"\n📂 Creating clean dist directory...")
    hf_dist = repo_root / "dist_hf"
    if hf_dist.exists():
        shutil.rmtree(hf_dist)
    hf_dist.mkdir()

    # Install wheel into dist_hf
    print(f"📥 Installing wheel to dist_hf...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", str(wheel_file), "--target", str(hf_dist)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ Installation failed:")
        print(result.stderr)
        return False

    print(f"✅ Wheel installed to dist_hf/")

    # Export requirements
    print(f"\n📋 Exporting requirements...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        capture_output=True,
        text=True
    )

    # Filter to only project dependencies (from pyproject.toml)
    requirements = [
        "gradio>=4.0.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "sentence-transformers>=2.2.0",
        "faiss-cpu>=1.7.0",
        "huggingface-hub>=0.17.0",
    ]

    requirements_file = hf_dist / "requirements.txt"
    with open(requirements_file, "w") as f:
        f.write("\n".join(requirements) + "\n")

    print(f"✅ Requirements written to requirements.txt")

    # Create entry point app.py
    print(f"\n🚀 Creating entry point app.py...")
    app_py = hf_dist / "app.py"
    app_py.write_text(
        """\"\"\"Entry point for Hugging Face Spaces.\"\"\"

import sys
from pathlib import Path

# Add the current directory to Python path so we can import the installed package
sys.path.insert(0, str(Path(__file__).parent))

from chatbot.app import demo

if __name__ == "__main__":
    demo.launch()
"""
    )
    print(f"✅ Entry point created")

    # Copy supporting files
    print(f"\n📄 Copying supporting files...")
    for filename in ["faq.md", "README.md"]:
        src = repo_root / filename
        if src.exists():
            dst = hf_dist / filename
            shutil.copy(src, dst)
            print(f"   ✅ {filename}")
        else:
            print(f"   ⚠️  {filename} not found")

    # Move dist_hf to dist
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    shutil.move(str(hf_dist), str(dist_dir))

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
