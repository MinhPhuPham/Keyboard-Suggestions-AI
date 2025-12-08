#!/bin/bash

# Complete automated build pipeline
# Installs dependencies → Trains model → Exports → Builds iOS/Android packages

set -e  # Exit on error

echo "========================================="
echo "Keyboard AI - Complete Build Pipeline"
echo "========================================="
echo ""

# Configuration
SKIP_INSTALL=false
SKIP_TRAINING=false
EPOCHS=50

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        --skip-training)
            SKIP_TRAINING=true
            shift
            ;;
        --epochs)
            EPOCHS="$2"
            shift 2
            ;;
        --quick)
            EPOCHS=5
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--skip-install] [--skip-training] [--epochs N] [--quick]"
            exit 1
            ;;
    esac
done

# Track start time
START_TIME=$(date +%s)

# Step 1: Install dependencies
if [ "$SKIP_INSTALL" = false ]; then
    echo "Step 1/6: Installing dependencies..."
    echo "-------------------------------------"
    
    if pip install -r requirements.txt > /tmp/pip_install.log 2>&1; then
        echo "✓ Dependencies installed"
    else
        echo "✗ Failed to install dependencies"
        echo "See /tmp/pip_install.log for details"
        exit 1
    fi
    echo ""
else
    echo "Step 1/6: Skipping dependency installation"
    echo ""
fi

# Step 2: Prepare training data
if [ "$SKIP_TRAINING" = false ]; then
    echo "Step 2/6: Preparing training data..."
    echo "-------------------------------------"
    
    if python3 src/utils/data_prep.py > /tmp/data_prep.log 2>&1; then
        LINES=$(wc -l < data/processed/combined_train.txt | tr -d ' ')
        echo "✓ Data prepared: $LINES training samples"
    else
        echo "✗ Data preparation failed"
        echo "See /tmp/data_prep.log for details"
        exit 1
    fi
    echo ""
else
    echo "Step 2/6: Skipping data preparation"
    echo ""
fi

# Step 3: Train tokenizer
if [ "$SKIP_TRAINING" = false ]; then
    echo "Step 3/6: Training tokenizer..."
    echo "-------------------------------------"
    
    if python3 src/tokenizer/train_tokenizer.py > /tmp/tokenizer.log 2>&1; then
        SIZE=$(du -h models/tokenizer.model | cut -f1)
        VOCAB=$(python3 -c "import sentencepiece as spm; sp = spm.SentencePieceProcessor(); sp.load('models/tokenizer.model'); print(sp.vocab_size())")
        echo "✓ Tokenizer trained: $SIZE, vocab=$VOCAB"
    else
        echo "✗ Tokenizer training failed"
        echo "See /tmp/tokenizer.log for details"
        exit 1
    fi
    echo ""
else
    echo "Step 3/6: Skipping tokenizer training"
    echo ""
fi

# Step 4: Train model
if [ "$SKIP_TRAINING" = false ]; then
    echo "Step 4/6: Training model ($EPOCHS epochs)..."
    echo "-------------------------------------"
    
    if python3 src/model/train.py --epochs $EPOCHS > /tmp/training.log 2>&1; then
        SIZE=$(du -h models/best_model.pt | cut -f1)
        # Extract best validation loss from training history
        BEST_LOSS=$(python3 -c "import json; data=json.load(open('models/training_history.json')); print(f\"{min(data['val_loss']):.4f}\")" 2>/dev/null || echo "N/A")
        echo "✓ Model trained: $SIZE, best val_loss=$BEST_LOSS"
    else
        echo "✗ Model training failed"
        echo "See /tmp/training.log for details"
        exit 1
    fi
    echo ""
else
    echo "Step 4/6: Skipping model training"
    echo ""
fi

# Step 5: Export model
echo "Step 5/6: Exporting model..."
echo "-------------------------------------"

if python3 src/utils/export_model.py > /tmp/export.log 2>&1; then
    SIZE=$(du -h models/mobile/tiny_lstm.pt | cut -f1)
    echo "✓ Model exported: $SIZE (TorchScript)"
else
    echo "✗ Model export failed"
    echo "See /tmp/export.log for details"
    exit 1
fi
echo ""

# Step 6: Build mobile packages
echo "Step 6/6: Building mobile packages..."
echo "-------------------------------------"

# Create package directories
mkdir -p ios/KeyboardAI
mkdir -p android/KeyboardAI

# Copy files to iOS package
echo "Building iOS package..."
cp models/mobile/tiny_lstm.pt ios/KeyboardAI/
cp models/tokenizer.model ios/KeyboardAI/
cp models/tokenizer.vocab ios/KeyboardAI/
cp config/language_rules.yaml ios/KeyboardAI/
cp config/custom_dictionary.json ios/KeyboardAI/

# Create iOS metadata
cat > ios/KeyboardAI/model_info.json << EOF
{
  "model_name": "KeyboardAI",
  "version": "1.0.0",
  "format": "TorchScript",
  "model_file": "tiny_lstm.pt",
  "tokenizer_file": "tokenizer.model",
  "vocab_file": "tokenizer.vocab",
  "model_size_mb": $(du -m models/mobile/tiny_lstm.pt | cut -f1),
  "tokenizer_size_kb": $(du -k models/tokenizer.model | cut -f1),
  "vocab_size": $(python3 -c "import sentencepiece as spm; sp = spm.SentencePieceProcessor(); sp.load('models/tokenizer.model'); print(sp.vocab_size())"),
  "min_ios_version": "12.0",
  "framework": "PyTorch Mobile",
  "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

# Create iOS README
cat > ios/KeyboardAI/README.md << 'EOF'
# KeyboardAI iOS Package

## Files Included

- `tiny_lstm.pt` - TorchScript model
- `tokenizer.model` - SentencePiece tokenizer
- `tokenizer.vocab` - Vocabulary file
- `language_rules.yaml` - Language-specific rules
- `custom_dictionary.json` - Custom dictionary
- `model_info.json` - Model metadata

## Integration

See `../../docs/integration/IOS_INTEGRATION.md` for detailed instructions.

## Requirements

- iOS 12.0+
- PyTorch Mobile framework

## Quick Start

1. Add all files to your Xcode project
2. Install PyTorch Mobile via CocoaPods or SPM
3. Load model: `let model = try! TorchModule(fileAtPath: path)`
4. See integration guide for complete implementation
EOF

# Copy files to Android package
echo "Building Android package..."
cp models/mobile/tiny_lstm.pt android/KeyboardAI/
cp models/tokenizer.model android/KeyboardAI/
cp models/tokenizer.vocab android/KeyboardAI/
cp config/language_rules.yaml android/KeyboardAI/
cp config/custom_dictionary.json android/KeyboardAI/

# Create Android metadata
cat > android/KeyboardAI/model_info.json << EOF
{
  "model_name": "KeyboardAI",
  "version": "1.0.0",
  "format": "TorchScript",
  "model_file": "tiny_lstm.pt",
  "tokenizer_file": "tokenizer.model",
  "vocab_file": "tokenizer.vocab",
  "model_size_mb": $(du -m models/mobile/tiny_lstm.pt | cut -f1),
  "tokenizer_size_kb": $(du -k models/tokenizer.model | cut -f1),
  "vocab_size": $(python3 -c "import sentencepiece as spm; sp = spm.SentencePieceProcessor(); sp.load('models/tokenizer.model'); print(sp.vocab_size())"),
  "min_android_api": 21,
  "framework": "PyTorch Mobile",
  "build_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

# Create Android README
cat > android/KeyboardAI/README.md << 'EOF'
# KeyboardAI Android Package

## Files Included

- `tiny_lstm.pt` - TorchScript model
- `tokenizer.model` - SentencePiece tokenizer
- `tokenizer.vocab` - Vocabulary file
- `language_rules.yaml` - Language-specific rules
- `custom_dictionary.json` - Custom dictionary
- `model_info.json` - Model metadata

## Integration

See `../../docs/integration/ANDROID_INTEGRATION.md` for detailed instructions.

## Requirements

- Android API 21+ (Android 5.0+)
- PyTorch Mobile for Android

## Quick Start

1. Add all files to `app/src/main/assets/`
2. Add PyTorch Mobile dependency to build.gradle
3. Load model: `Module module = LiteModuleLoader.load(assetFilePath(this, "tiny_lstm.pt"))`
4. See integration guide for complete implementation
EOF

# Create zip packages
echo "Creating deployment packages..."
cd ios && zip -r KeyboardAI-iOS-Package.zip KeyboardAI/ > /dev/null 2>&1 && cd ..
cd android && zip -r KeyboardAI-Android-Package.zip KeyboardAI/ > /dev/null 2>&1 && cd ..

IOS_SIZE=$(du -h ios/KeyboardAI-iOS-Package.zip | cut -f1)
ANDROID_SIZE=$(du -h android/KeyboardAI-Android-Package.zip | cut -f1)

echo "✓ iOS package created: $IOS_SIZE"
echo "✓ Android package created: $ANDROID_SIZE"
echo ""

# Calculate total time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

# Final summary
echo "========================================="
echo "✓ BUILD COMPLETE!"
echo "========================================="
echo ""
echo "Build time: ${MINUTES}m ${SECONDS}s"
echo ""
echo "Generated Packages:"
echo "  iOS:     ios/KeyboardAI-iOS-Package.zip ($IOS_SIZE)"
echo "  Android: android/KeyboardAI-Android-Package.zip ($ANDROID_SIZE)"
echo ""
echo "Package Contents:"
IOS_TOTAL=$(du -sh ios/KeyboardAI | cut -f1)
echo "  iOS package:     $IOS_TOTAL"
echo "    - tiny_lstm.pt (TorchScript model)"
echo "    - tokenizer.model + .vocab"
echo "    - language_rules.yaml"
echo "    - custom_dictionary.json"
echo "    - model_info.json"
echo ""
ANDROID_TOTAL=$(du -sh android/KeyboardAI | cut -f1)
echo "  Android package: $ANDROID_TOTAL"
echo "    - tiny_lstm.pt (TorchScript model)"
echo "    - tokenizer.model + .vocab"
echo "    - language_rules.yaml"
echo "    - custom_dictionary.json"
echo "    - model_info.json"
echo ""
echo "Next Steps:"
echo "  1. Extract packages to your iOS/Android projects"
echo "  2. Follow integration guides in docs/integration/"
echo "  3. Test on devices and report performance"
echo ""
echo "Integration Guides:"
echo "  - iOS:     docs/integration/IOS_INTEGRATION.md"
echo "  - Android: docs/integration/ANDROID_INTEGRATION.md"
echo ""
