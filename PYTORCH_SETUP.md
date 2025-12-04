# PyTorch Installation with PDM

This project uses a custom solution to handle PyTorch installation due to PDM's limitations with PyTorch's platform-specific wheels.

## The Problem

PyTorch distributes platform-specific wheels through a custom index (https://download.pytorch.org/whl/). PDM's dependency resolution struggles with this because:
- Without package filtering, PDM tries to fetch all packages from the PyTorch index (fails)
- `include_packages` feature doesn't exist in PDM 2.26.x
- Existing plugins like `pdm-plugin-torch` are incompatible with current PDM versions
- Hash verification fails when PDM tries to install torch from PyPI

## The Solution

We exclude torch from PDM's dependency resolution and install it separately using a custom script:

### Configuration (`pyproject.toml`)

```toml
[tool.pdm.resolution]
# Exclude torch from PDM's dependency resolution
excludes = ["torch"]

[tool.pdm.scripts]
# Install all dependencies (automatically handles PyTorch)
install = {composite = ["pdm sync --no-self", "install-torch"]}
# Install PyTorch from the official index
install-torch = "python scripts/install_torch.py"
```

### Installation Script (`scripts/install_torch.py`)

The script:
1. Ensures pip is available in the venv
2. Installs PyTorch from the official CPU index
3. Handles platform-specific wheel selection automatically

## Usage

###For first-time setup:

```bash
pdm run install
```

This command will:
1. Lock dependencies (excluding torch)
2. Install all dependencies via PDM
3. Install PyTorch from the official index

### For regular pdm install:

If you just want to use standard `pdm install`:

```bash
pdm install  # Install PDM-managed dependencies
pdm run install-torch  # Then install PyTorch
```

## Why This Works

1. **Clean separation**: torch is completely excluded from PDM's lock file
2. **No hash conflicts**: PyTorch is installed directly via pip with its official index
3. **Platform-agnostic**: The script automatically selects the correct wheel for your platform
4. **Reliable**: Uses PyTorch's official distribution method
5. **Maintainable**: Single script, easy to update for different torch variants (CUDA, etc.)

## Customizing for CUDA/ROCm

To use CUDA or ROCm versions, edit `scripts/install_torch.py`:

```python
# For CUDA 11.8
index_url = "https://download.pytorch.org/whl/cu118"

# For CUDA 12.1
index_url = "https://download.pytorch.org/whl/cu121"

# For ROCm 5.7
index_url = "https://download.pytorch.org/whl/rocm5.7"
```

## Future Improvements

When PDM adds native support for per-package source configuration (the `include_packages` feature), we can migrate to that approach for a cleaner solution.
