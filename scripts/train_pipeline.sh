#!/bin/bash

# Complete pipeline script to train and export the keyboard AI model

echo "========================================="
echo "Keyboard Suggestions AI - Training Pipeline"
echo "========================================="

# Step 1: Create sample training data
echo ""
echo "Step 1: Creating sample training data..."
python3 src/utils/data_prep.py

if [ $? -ne 0 ]; then
    echo "Error: Failed to create training data"
    exit 1
fi

# Step 2: Train tokenizer
echo ""
echo "Step 2: Training SentencePiece tokenizer..."
python3 src/tokenizer/train_tokenizer.py

if [ $? -ne 0 ]; then
    echo "Error: Failed to train tokenizer"
    exit 1
fi

# Step 3: Create custom dictionary
echo ""
echo "Step 3: Creating custom dictionary..."
python3 src/dictionary/custom_dict.py

if [ $? -ne 0 ]; then
    echo "Error: Failed to create custom dictionary"
    exit 1
fi

# Step 4: Train model
echo ""
echo "Step 4: Training TinyLSTM model..."
python3 src/model/train.py

if [ $? -ne 0 ]; then
    echo "Error: Failed to train model"
    exit 1
fi

# Step 5: Export model for mobile
echo ""
echo "Step 5: Exporting model for mobile deployment..."
python3 src/utils/export_model.py

if [ $? -ne 0 ]; then
    echo "Error: Failed to export model"
    exit 1
fi

# Step 6: Test prediction engine
echo ""
echo "Step 6: Testing prediction engine..."
python3 src/inference/prediction_engine.py

if [ $? -ne 0 ]; then
    echo "Error: Failed to test prediction engine"
    exit 1
fi

echo ""
echo "========================================="
echo "✓ Pipeline completed successfully!"
echo "========================================="
echo ""
echo "Generated files:"
echo "  - models/tokenizer.model (SentencePiece tokenizer)"
echo "  - models/best_model.pt (Trained PyTorch model)"
echo "  - models/mobile/tiny_lstm.onnx (ONNX model)"
echo "  - models/mobile/tiny_lstm_int8.onnx (Quantized model)"
echo "  - config/custom_dictionary.json (Custom dictionary)"
echo ""
echo "Next steps:"
echo "  1. Integrate ONNX model into iOS/Android app"
echo "  2. Copy tokenizer.model and custom_dictionary.json to app"
echo "  3. Test on mobile devices"
