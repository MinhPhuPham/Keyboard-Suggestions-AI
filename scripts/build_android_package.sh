#!/bin/bash

# Build complete Android deployment package

echo "========================================="
echo "Building Android Deployment Package"
echo "========================================="

# Check if ONNX model exists
if [ ! -f "models/mobile/tiny_lstm.onnx" ]; then
    echo "Error: ONNX model not found"
    echo "Please export to ONNX first:"
    echo "  python src/utils/export_model.py"
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
mkdir -p android/KeyboardAI

echo ""
echo "Step 1: Exporting model to TensorFlow Lite..."
python3 scripts/export_tflite.py \
    --model models/mobile/tiny_lstm.onnx \
    --output android/KeyboardAI \
    --name keyboard_ai

if [ $? -ne 0 ]; then
    echo "Error: TFLite export failed"
    echo "Make sure dependencies are installed:"
    echo "  pip install onnx onnx-tf tensorflow"
    exit 1
fi

echo ""
echo "Step 2: Copying tokenizer..."
cp models/tokenizer.model android/KeyboardAI/
cp models/tokenizer.vocab android/KeyboardAI/
echo "  ✓ Tokenizer copied"

echo ""
echo "Step 3: Copying configuration files..."
cp config/language_rules.yaml android/KeyboardAI/
cp config/custom_dictionary.json android/KeyboardAI/
echo "  ✓ Configuration files copied"

echo ""
echo "Step 4: Creating package info..."
cat > android/KeyboardAI/README.md << 'EOF'
# KeyboardAI Android Package

This package contains all necessary files for Android keyboard integration.

## Files Included

- `keyboard_ai_int8.tflite` - TensorFlow Lite model (INT8 quantized)
- `tokenizer.model` - SentencePiece tokenizer
- `tokenizer.vocab` - Tokenizer vocabulary
- `language_rules.yaml` - Language-specific rules (EN/JA)
- `custom_dictionary.json` - Custom dictionary entries
- `model_info.json` - Model metadata

## Integration

See `docs/integration/ANDROID_INTEGRATION.md` for detailed integration instructions.

## Requirements

- Android API 21+ (Android 5.0+)
- TensorFlow Lite runtime
- SentencePiece JNI bindings

## Model Info

- Input: Token IDs (Int32 array)
- Output: Logits for next token prediction
- Quantization: INT8
- Vocab Size: Check model_info.json

## Quick Start

1. Add TFLite model to assets folder
2. Copy tokenizer files to assets
3. Load model with TFLite Interpreter
4. See integration guide for Kotlin/Java code examples
EOF

echo "  ✓ README created"

# Create a zip package
echo ""
echo "Step 5: Creating deployment package..."
cd android
zip -r KeyboardAI-Android-Package.zip KeyboardAI/ > /dev/null 2>&1
cd ..

PACKAGE_SIZE=$(du -h android/KeyboardAI-Android-Package.zip | cut -f1)

echo "  ✓ Package created: android/KeyboardAI-Android-Package.zip"
echo "  Size: $PACKAGE_SIZE"

echo ""
echo "========================================="
echo "✓ Android Package Build Complete!"
echo "========================================="
echo ""
echo "Package location: android/KeyboardAI/"
echo "Deployment zip: android/KeyboardAI-Android-Package.zip"
echo ""
echo "Next steps:"
echo "  1. Review integration guide: docs/integration/ANDROID_INTEGRATION.md"
echo "  2. Import package into your Android project"
echo "  3. Follow Kotlin/Java integration examples"
echo "  4. Test and provide performance feedback"
