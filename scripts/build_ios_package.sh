#!/bin/bash

# Build complete iOS deployment package

echo "========================================="
echo "Building iOS Deployment Package"
echo "========================================="

# Check if model is trained
if [ ! -f "models/best_model.pt" ]; then
    echo "Error: Trained model not found at models/best_model.pt"
    echo "Please train the model first:"
    echo "  python src/model/train.py"
    exit 1
fi

# Check if tokenizer exists
if [ ! -f "models/tokenizer.model" ]; then
    echo "Error: Tokenizer not found at models/tokenizer.model"
    echo "Please train the tokenizer first:"
    echo "  python src/tokenizer/train_tokenizer.py"
    exit 1
fi

# Create output directory
mkdir -p ios/KeyboardAI

echo ""
echo "Step 1: Exporting model to Core ML..."
python3 scripts/export_coreml.py \
    --model models/best_model.pt \
    --output ios/KeyboardAI \
    --name KeyboardAI

if [ $? -ne 0 ]; then
    echo "Error: Core ML export failed"
    echo "Make sure coremltools is installed:"
    echo "  pip install coremltools"
    exit 1
fi

echo ""
echo "Step 2: Copying tokenizer..."
cp models/tokenizer.model ios/KeyboardAI/
cp models/tokenizer.vocab ios/KeyboardAI/
echo "  ✓ Tokenizer copied"

echo ""
echo "Step 3: Copying configuration files..."
cp config/language_rules.yaml ios/KeyboardAI/
cp config/custom_dictionary.json ios/KeyboardAI/
echo "  ✓ Configuration files copied"

echo ""
echo "Step 4: Creating package info..."
cat > ios/KeyboardAI/README.md << 'EOF'
# KeyboardAI iOS Package

This package contains all necessary files for iOS keyboard integration.

## Files Included

- `KeyboardAI.mlpackage` - Core ML model for next-word prediction
- `tokenizer.model` - SentencePiece tokenizer
- `tokenizer.vocab` - Tokenizer vocabulary
- `language_rules.yaml` - Language-specific rules (EN/JA)
- `custom_dictionary.json` - Custom dictionary entries
- `model_info.json` - Model metadata

## Integration

See `docs/integration/IOS_INTEGRATION.md` for detailed integration instructions.

## Requirements

- iOS 15.0+
- Xcode 13.0+
- Swift 5.5+

## Model Info

- Input: Token IDs (Int array)
- Output: Logits for next token prediction
- Vocab Size: Check model_info.json
- Precision: FLOAT16

## Quick Start

1. Add KeyboardAI.mlpackage to your Xcode project
2. Copy tokenizer files to app bundle
3. Load model with Core ML
4. See integration guide for Swift code examples
EOF

echo "  ✓ README created"

# Create a zip package
echo ""
echo "Step 5: Creating deployment package..."
cd ios
zip -r KeyboardAI-iOS-Package.zip KeyboardAI/ > /dev/null 2>&1
cd ..

PACKAGE_SIZE=$(du -h ios/KeyboardAI-iOS-Package.zip | cut -f1)

echo "  ✓ Package created: ios/KeyboardAI-iOS-Package.zip"
echo "  Size: $PACKAGE_SIZE"

echo ""
echo "========================================="
echo "✓ iOS Package Build Complete!"
echo "========================================="
echo ""
echo "Package location: ios/KeyboardAI/"
echo "Deployment zip: ios/KeyboardAI-iOS-Package.zip"
echo ""
echo "Next steps:"
echo "  1. Review integration guide: docs/integration/IOS_INTEGRATION.md"
echo "  2. Import package into your iOS project"
echo "  3. Follow Swift integration examples"
echo "  4. Test and provide performance feedback"
