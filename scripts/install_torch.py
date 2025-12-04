#!/usr/bin/env python3
"""Install PyTorch from the official PyTorch index."""

import subprocess
import sys


def main():
    """Install torch using the PyTorch official index."""
    print("Installing PyTorch from official CPU index...")

    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "pip",  # Ensure pip is available
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        # pip might not be installed, install it via ensurepip
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
        subprocess.run(cmd, check=True, capture_output=True)

    # Now install torch
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "torch>=2.2.0",
        "--index-url",
        "https://download.pytorch.org/whl/cpu",
    ]

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print("✓ PyTorch installed successfully!")
    else:
        print("✗ Failed to install PyTorch")
        sys.exit(1)


if __name__ == "__main__":
    main()
