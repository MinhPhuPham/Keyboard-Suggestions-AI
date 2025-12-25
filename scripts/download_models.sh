#!/bin/bash

# Download pre-trained models from GitHub releases
# Models are too large for git, so they're distributed via releases

set -e

echo "========================================"
echo "Downloading Pre-trained Models"
echo "========================================"
echo ""

# Configuration
GITHUB_REPO="MinhPhuPham/Keyboard-Suggestions-AI"
RELEASE_TAG="v1.0.0"  # Update this to latest release
MODELS_DIR="models"

# Create models directory
mkdir -p "$MODELS_DIR"

# Function to download file
download_file() {
    local filename=$1
    local url="https://github.com/${GITHUB_REPO}/releases/download/${RELEASE_TAG}/${filename}"
    
    echo "Downloading $filename..."
    
    if command -v curl &> /dev/null; then
        curl -L -o "${MODELS_DIR}/${filename}" "$url"
    elif command -v wget &> /dev/null; then
        wget -O "${MODELS_DIR}/${filename}" "$url"
    else
        echo "Error: Neither curl nor wget found. Please install one of them."
        exit 1
    fi
    
    echo "✓ Downloaded $filename"
}

# Check if models already exist
if [ -f "${MODELS_DIR}/KeyboardAI_Japanese.mlpackage" ]; then
    echo "⚠️  Models already exist in ${MODELS_DIR}/"
    read -p "Do you want to re-download? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping download."
        exit 0
    fi
fi

echo "Downloading models from GitHub releases..."
echo "Repository: ${GITHUB_REPO}"
echo "Release: ${RELEASE_TAG}"
echo ""

# Download files
download_file "KeyboardAI_Japanese.mlpackage.zip"
download_file "tokenizer.vocab"
download_file "model_info.json"

# Extract Core ML package
echo ""
echo "Extracting Core ML package..."
cd "$MODELS_DIR"
unzip -q KeyboardAI_Japanese.mlpackage.zip
rm KeyboardAI_Japanese.mlpackage.zip
cd ..

echo ""
echo "========================================"
echo "✅ Download Complete!"
echo "========================================"
echo ""
echo "Downloaded files:"
ls -lh "${MODELS_DIR}/" | grep -v "^total" | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "Next steps:"
echo "  1. Test the model: python src/keyboard_handler.py"
echo "  2. Run tests: python scripts/test_predictive_text.py"
echo "  3. Build for iOS: ./scripts/build_ios_package.sh"
echo ""
