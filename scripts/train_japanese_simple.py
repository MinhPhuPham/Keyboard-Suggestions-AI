#!/usr/bin/env python3
"""
Simple Japanese model training script
"""

import sys
import torch
import sentencepiece as spm
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path.cwd()))

from src.tokenizer.train_tokenizer import TokenizerTrainer
from src.model.tiny_lstm import TinyLSTM
import subprocess

def main():
    print("="*70)
    print("TRAINING JAPANESE MODEL")
    print("="*70)
    print()
    
    # Create directories
    Path('models/japanese').mkdir(parents=True, exist_ok=True)
    
    # Step 1: Train tokenizer
    print("Step 1: Training tokenizer...")
    trainer = TokenizerTrainer()
    trainer.train(
        input_files=['data/processed/comprehensive_train.txt'],
        vocab_size=32000,
        character_coverage=0.9995,
        model_type='unigram'
    )
    
    # Copy to Japanese directory
    import shutil
    shutil.copy('models/tokenizer.model', 'models/japanese/tokenizer.model')
    shutil.copy('models/tokenizer.vocab', 'models/japanese/tokenizer.vocab')
    print("✅ Tokenizer trained and copied")
    print()
    
    # Step 2: Train model
    print("Step 2: Training model...")
    print("Running: python src/model/train.py")
    print()
    
    result = subprocess.run([
        sys.executable, 'src/model/train.py',
        '--data-file', 'data/processed/comprehensive_train.txt',
        '--epochs', '30'
    ])
    
    if result.returncode != 0:
        print("❌ Training failed")
        sys.exit(1)
    
    # Copy to Japanese directory
    shutil.copy('models/best_model.pt', 'models/japanese/best_model.pt')
    shutil.copy('models/training_history.json', 'models/japanese/training_history.json')
    print()
    print("✅ Model trained and copied")
    print()
    
    # Step 3: Export to Core ML
    print("Step 3: Exporting to Core ML...")
    result = subprocess.run([
        sys.executable, 'scripts/export_coreml.py'
    ])
    
    if result.returncode != 0:
        print("❌ Export failed")
        sys.exit(1)
    
    # Move to Japanese directory
    Path('ios/KeyboardAI/Japanese').mkdir(parents=True, exist_ok=True)
    shutil.move('ios/KeyboardAI/KeyboardAI.mlpackage', 'ios/KeyboardAI/Japanese/KeyboardAI_Japanese.mlpackage')
    shutil.copy('models/japanese/tokenizer.model', 'ios/KeyboardAI/Japanese/')
    shutil.copy('models/japanese/tokenizer.vocab', 'ios/KeyboardAI/Japanese/')
    
    # Create model info
    import json
    model_info = {
        'language': 'japanese',
        'vocab_size': 32000,
        'model_version': '1.0.0',
        'embedding_dim': 128,
        'hidden_dim': 256
    }
    with open('ios/KeyboardAI/Japanese/model_info.json', 'w') as f:
        json.dump(model_info, f, indent=2)
    
    print()
    print("="*70)
    print("✅ JAPANESE MODEL COMPLETE!")
    print("="*70)
    print()
    print("Files created:")
    print("  models/japanese/best_model.pt")
    print("  models/japanese/tokenizer.{model,vocab}")
    print("  ios/KeyboardAI/Japanese/KeyboardAI_Japanese.mlpackage")
    print()
    print("Next: Test the model")
    print("  python scripts/test_japanese_ime.py")
    print()

if __name__ == '__main__':
    main()
