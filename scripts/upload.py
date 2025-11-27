"""Upload distribution to Hugging Face Space."""

import sys
import os
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_file


def main():
    """Upload dist/ directory to Hugging Face Space."""
    repo_root = Path(__file__).parent.parent
    dist_dir = repo_root / "dist"

    # Get credentials
    if len(sys.argv) < 3:
        print("Usage: pdm run upload USERNAME SPACE_NAME")
        print("\nExample:")
        print("  pdm run upload myusername my-store-chatbot")
        print("\nMake sure you've logged in first:")
        print("  huggingface-cli login")
        sys.exit(1)

    username = sys.argv[1]
    space_name = sys.argv[2]

    # Check for optional token argument
    token = None
    if "--token" in sys.argv:
        token_idx = sys.argv.index("--token")
        if token_idx + 1 < len(sys.argv):
            token = sys.argv[token_idx + 1]

    # Verify dist directory exists
    if not dist_dir.exists():
        print(f"❌ Error: dist/ directory not found")
        print(f"   Run 'pdm run build' first to create the distribution")
        sys.exit(1)

    repo_id = f"{username}/{space_name}"

    print("=" * 60)
    print(f"Uploading to Hugging Face Space: {repo_id}")
    print("=" * 60)

    # Initialize API
    api = HfApi(token=token)

    # Create Space
    print(f"\n📦 Creating/verifying Space...")
    try:
        create_repo(
            repo_id=repo_id,
            token=token,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True
        )
        print(f"✅ Space ready: https://huggingface.co/spaces/{repo_id}")
    except Exception as e:
        print(f"❌ Error creating Space: {e}")
        return False

    # Upload files
    print(f"\n📤 Uploading files...")

    files_uploaded = 0
    for item in sorted(dist_dir.iterdir()):
        if item.is_file():
            try:
                upload_file(
                    path_or_fileobj=str(item),
                    path_in_repo=item.name,
                    repo_id=repo_id,
                    repo_type="space",
                    token=token
                )
                print(f"   ✅ {item.name}")
                files_uploaded += 1
            except Exception as e:
                print(f"   ❌ {item.name}: {e}")
                return False
        elif item.is_dir():
            # Upload directory contents recursively
            for file_path in item.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(dist_dir)
                    try:
                        upload_file(
                            path_or_fileobj=str(file_path),
                            path_in_repo=str(rel_path),
                            repo_id=repo_id,
                            repo_type="space",
                            token=token
                        )
                        print(f"   ✅ {rel_path}")
                        files_uploaded += 1
                    except Exception as e:
                        print(f"   ❌ {rel_path}: {e}")
                        return False

    print(f"\n" + "=" * 60)
    print(f"✅ Success! Uploaded {files_uploaded} files")
    print(f"=" * 60)
    print(f"\n🚀 Your chatbot is deploying at:")
    print(f"   https://huggingface.co/spaces/{repo_id}")
    print(f"\n⏳ Wait a few minutes for the Space to build, then visit the URL above.")
    print(f"\n💡 Tip: Watch the build logs in the 'Logs' tab if you encounter issues.")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
