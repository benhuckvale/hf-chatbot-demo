#!/usr/bin/env python3
"""
Upload chatbot files to Hugging Face Space using the Hub API

Usage:
    1. Install huggingface_hub: pip install huggingface_hub
    2. Login: huggingface-cli login
    3. Run: python upload_to_hf.py YOUR-USERNAME YOUR-SPACE-NAME

Alternative: Pass token directly
    python upload_to_hf.py YOUR-USERNAME YOUR-SPACE-NAME --token YOUR_HF_TOKEN
"""

import sys
import os
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_file

def upload_chatbot_to_hf(username, space_name, token=None):
    """
    Upload all chatbot files to a Hugging Face Space
    
    Args:
        username: Your HF username
        space_name: Name for your Space
        token: HF token (optional if logged in via CLI)
    """
    
    # Initialize the API
    api = HfApi(token=token)
    
    # Create the repo_id (format: username/space_name)
    repo_id = f"{username}/{space_name}"
    
    print(f"Creating Space: {repo_id}")
    
    try:
        # Create the Space (repo_type="space")
        create_repo(
            repo_id=repo_id,
            token=token,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True  # Don't fail if already exists
        )
        print(f"✅ Space created/verified: https://huggingface.co/spaces/{repo_id}")
        
    except Exception as e:
        print(f"❌ Error creating Space: {e}")
        return False
    
    # Files to upload
    files_to_upload = [
        "app.py",
        "requirements.txt", 
        "faq.md",
        "README.md"
    ]
    
    print("\nUploading files...")
    
    for filename in files_to_upload:
        if not os.path.exists(filename):
            print(f"⚠️  Warning: {filename} not found, skipping")
            continue
            
        try:
            upload_file(
                path_or_fileobj=filename,
                path_in_repo=filename,
                repo_id=repo_id,
                repo_type="space",
                token=token
            )
            print(f"✅ Uploaded: {filename}")
            
        except Exception as e:
            print(f"❌ Error uploading {filename}: {e}")
            return False
    
    print(f"\n🎉 Success! Your chatbot is deploying at:")
    print(f"   https://huggingface.co/spaces/{repo_id}")
    print(f"\n⏳ Wait a few minutes for the Space to build, then visit the URL above.")
    print(f"\n💡 Tip: Watch the build logs in the 'Logs' tab if you encounter issues.")
    
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python upload_to_hf.py USERNAME SPACE_NAME [--token TOKEN]")
        print("\nExample:")
        print("  python upload_to_hf.py myusername my-store-chatbot")
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
    
    # Change to the directory containing the files
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success = upload_chatbot_to_hf(username, space_name, token)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
