#!/bin/bash

# Master build script for creating both iOS and Android packages

echo "========================================="
echo "KeyboardAI - Mobile Package Builder"
echo "========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi

# Check if model is trained
if [ ! -f "models/best_model.pt" ]; then
    echo "⚠️  Warning: Trained model not found"
    echo "   You need to train the model first:"
    echo "   python src/model/train.py"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if tokenizer exists
if [ ! -f "models/tokenizer.model" ]; then
    echo "Error: Tokenizer not found"
    echo "Please train the tokenizer first:"
    echo "  python src/tokenizer/train_tokenizer.py"
    exit 1
fi

echo "✓ Prerequisites check passed"
echo ""

# Menu
echo "Select build target:"
echo "  1) iOS package only"
echo "  2) Android package only"
echo "  3) Both iOS and Android"
echo "  4) Export models only (ONNX + quantization)"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "Building iOS package..."
        ./scripts/build_ios_package.sh
        ;;
    2)
        echo ""
        echo "Building Android package..."
        
        # First export to ONNX if needed
        if [ ! -f "models/mobile/tiny_lstm.onnx" ]; then
            echo "Exporting model to ONNX first..."
            python3 src/utils/export_model.py
        fi
        
        ./scripts/build_android_package.sh
        ;;
    3)
        echo ""
        echo "Building both packages..."
        
        # Export to ONNX first
        if [ ! -f "models/mobile/tiny_lstm.onnx" ]; then
            echo "Step 1: Exporting model to ONNX..."
            python3 src/utils/export_model.py
            echo ""
        fi
        
        # Build iOS
        echo "Step 2: Building iOS package..."
        ./scripts/build_ios_package.sh
        echo ""
        
        # Build Android
        echo "Step 3: Building Android package..."
        ./scripts/build_android_package.sh
        ;;
    4)
        echo ""
        echo "Exporting models..."
        python3 src/utils/export_model.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "Build Summary"
echo "========================================="

# Show what was created
if [ -d "ios/KeyboardAI" ]; then
    echo ""
    echo "iOS Package:"
    echo "  Location: ios/KeyboardAI/"
    if [ -f "ios/KeyboardAI-iOS-Package.zip" ]; then
        IOS_SIZE=$(du -h ios/KeyboardAI-iOS-Package.zip | cut -f1)
        echo "  Package: ios/KeyboardAI-iOS-Package.zip ($IOS_SIZE)"
    fi
    echo "  Integration: docs/integration/IOS_INTEGRATION.md"
fi

if [ -d "android/KeyboardAI" ]; then
    echo ""
    echo "Android Package:"
    echo "  Location: android/KeyboardAI/"
    if [ -f "android/KeyboardAI-Android-Package.zip" ]; then
        ANDROID_SIZE=$(du -h android/KeyboardAI-Android-Package.zip | cut -f1)
        echo "  Package: android/KeyboardAI-Android-Package.zip ($ANDROID_SIZE)"
    fi
    echo "  Integration: docs/integration/ANDROID_INTEGRATION.md"
fi

echo ""
echo "========================================="
echo "Next Steps"
echo "========================================="
echo ""
echo "1. Review integration guides in docs/integration/"
echo "2. Import packages into your mobile projects"
echo "3. Follow platform-specific setup instructions"
echo "4. Test and measure performance"
echo "5. Provide feedback on:"
echo "   - Prediction latency"
echo "   - Memory usage"
echo "   - Model accuracy"
echo "   - Integration issues"
echo ""
