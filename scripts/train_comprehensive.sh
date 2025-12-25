#!/bin/bash
#
# Automated training pipeline for comprehensive dataset
# This script handles: data collection → tokenizer training → model training → Core ML export
#

set -e  # Exit on error

echo "======================================================================"
echo "AUTOMATED TRAINING PIPELINE"
echo "======================================================================"
echo ""

# Activate Python environment
echo "🐍 Activating Python environment..."
source .venv-coreml/bin/activate
echo "   ✓ Environment activated"
echo ""

# Step 1: Collect all data
echo "======================================================================"
echo "STEP 1: DATA COLLECTION"
echo "======================================================================"
python scripts/collect_all_data.py
echo ""

# Step 2: Train tokenizer
echo "======================================================================"
echo "STEP 2: TOKENIZER TRAINING"
echo "======================================================================"
echo "Training tokenizer on comprehensive dataset..."
echo "  Vocab size: 32,000"
echo "  Coverage: 0.9995"
echo "  This will take 5-10 minutes..."
echo ""

python -c "
from src.tokenizer.train_tokenizer import TokenizerTrainer

trainer = TokenizerTrainer()
trainer.train(
    input_files=['data/processed/comprehensive_train.txt'],
    vocab_size=32000,
    character_coverage=0.9995,
    model_type='unigram'
)

print()
print('✅ Tokenizer training complete!')
"

echo ""

# Step 3: Update config for comprehensive training
echo "======================================================================"
echo "STEP 3: CONFIGURATION"
echo "======================================================================"
echo "Updating model configuration..."

python -c "
import yaml

config = {
    'model': {
        'embedding_dim': 128,
        'hidden_dim': 256,
        'num_layers': 1,
        'dropout': 0.2,
        'vocab_size': 32000
    },
    'tokenizer': {
        'type': 'sentencepiece',
        'model_type': 'unigram',
        'vocab_size': 32000,
        'character_coverage': 0.9995
    },
    'data': {
        'max_sequence_length': 50,
        'train_file': 'data/processed/comprehensive_train.txt'
    },
    'training': {
        'batch_size': 128,  # Larger batch for more data
        'learning_rate': 0.001,
        'num_epochs': 30,   # Fewer epochs for large dataset
        'early_stopping_patience': 5,
        'val_split': 0.05,  # Smaller validation split
        'validation_split': 0.05,
        'gradient_clip': 1.0,
        'save_dir': 'models',
        'log_interval': 1000
    },
    'optimization': {
        'target_model_size_mb': 25
    }
}

with open('config/model_config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print('✅ Configuration updated')
print('   Dataset: 1.1M sentences')
print('   Batch size: 128')
print('   Epochs: 30')
"

echo ""

# Step 4: Train model
echo "======================================================================"
echo "STEP 4: MODEL TRAINING"
echo "======================================================================"
echo "Training model on comprehensive dataset..."
echo "  Dataset: 1,106,379 sentences"
echo "  Vocab: 32,000 tokens"
echo "  This will take 2-4 hours..."
echo ""
echo "⏰ Started at: $(date)"
echo ""

python src/model/train.py --data-file data/processed/comprehensive_train.txt --epochs 30

echo ""
echo "⏰ Finished at: $(date)"
echo ""

# Step 5: Export to Core ML
echo "======================================================================"
echo "STEP 5: CORE ML EXPORT"
echo "======================================================================"
echo "Exporting model to Core ML..."
echo ""

python scripts/export_coreml.py

echo ""

# Step 6: Copy files to iOS
echo "======================================================================"
echo "STEP 6: PREPARE iOS FILES"
echo "======================================================================"
echo "Copying files to iOS directory..."

cp models/tokenizer.model ios/KeyboardAI/
cp models/tokenizer.vocab ios/KeyboardAI/

echo "   ✓ tokenizer.model copied"
echo "   ✓ tokenizer.vocab copied"
echo ""

# Summary
echo "======================================================================"
echo "✅ TRAINING PIPELINE COMPLETE!"
echo "======================================================================"
echo ""
echo "📊 Results:"
echo "   Training data: 1,106,379 sentences"
echo "   Model: models/best_model.pt"
echo "   Core ML: ios/KeyboardAI/KeyboardAI.mlpackage"
echo "   Tokenizer: ios/KeyboardAI/tokenizer.{model,vocab}"
echo ""
echo "📱 Next steps:"
echo "   1. Open your iOS project in Xcode"
echo "   2. Add files from ios/KeyboardAI/ to your project"
echo "   3. Test on device"
echo ""
echo "🎉 Ready for iOS testing!"
echo "======================================================================"
