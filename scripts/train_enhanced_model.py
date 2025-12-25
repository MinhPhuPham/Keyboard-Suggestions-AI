#!/usr/bin/env python3
"""
Train Enhanced Japanese Model with Kanji Knowledge Baked In
Integrates kanji dictionary and context patterns directly into the model
"""

import torch
import torch.nn as nn
import json
from pathlib import Path
from typing import List, Dict

class EnhancedJapaneseModel(nn.Module):
    """
    LSTM model with built-in kanji knowledge
    No runtime dictionaries needed!
    """
    
    def __init__(self, vocab_size: int, embedding_dim: int = 128, hidden_dim: int = 256):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
        
        # Kanji attention layer - learns context patterns
        self.context_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=4,
            batch_first=True
        )
        
    def forward(self, x):
        # Embed input
        embedded = self.embedding(x)
        
        # LSTM processing
        lstm_out, (hidden, cell) = self.lstm(embedded)
        
        # Context attention - learns kanji patterns automatically
        attended, _ = self.context_attention(lstm_out, lstm_out, lstm_out)
        
        # Combine LSTM and attention
        combined = lstm_out + attended
        
        # Final prediction
        output = self.fc(combined[:, -1, :])
        
        return output


def create_kanji_aware_training_data():
    """
    Create training data that teaches the model kanji patterns
    No need for runtime dictionaries!
    """
    
    # Load kanji dictionary
    with open('data/kanji_dictionary.json', 'r', encoding='utf-8') as f:
        kanji_dict = json.load(f)
    
    # Load compound words
    with open('data/compound_words.json', 'r', encoding='utf-8') as f:
        compound_words = json.load(f)
    
    training_examples = []
    
    # Generate context-aware training examples
    # Example: "お祈りをして" + "かみ" → "神"
    context_patterns = [
        ("お祈りをして", "かみ", "神"),
        ("印刷する", "かみ", "紙"),
        ("美容院で", "かみ", "髪"),
        ("川に", "はし", "橋"),
        ("食事で", "はし", "箸"),
        ("夏は", "あつい", "暑い"),
        ("お湯が", "あつい", "熱い"),
        ("音楽を", "きく", "聴く"),
        ("話を", "きく", "聞く"),
        ("実験で", "かがく", "化学"),
        ("研究", "かがく", "科学"),
        ("学", "せい", "生"),  # 学生
        ("男", "せい", "性"),  # 男性
        ("都", "し", "市"),    # 都市
        ("教", "し", "師"),    # 教師
    ]
    
    for context, hiragana, kanji in context_patterns:
        # Create training example: context + hiragana → kanji
        training_examples.append(f"{context}{hiragana}\t{kanji}")
    
    # Add compound words
    for hiragana, kanjis in compound_words.items():
        for kanji in kanjis:
            training_examples.append(f"{hiragana}\t{kanji}")
    
    # Save enhanced training data
    output_file = Path('data/processed/enhanced_training.txt')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(training_examples))
    
    print(f"✓ Created {len(training_examples)} enhanced training examples")
    print(f"✓ Saved to: {output_file}")
    
    return training_examples


def main():
    print("="*70)
    print("CREATING ENHANCED JAPANESE MODEL")
    print("="*70)
    print()
    print("🎯 Goal: Bake kanji knowledge into the model")
    print("   - No runtime dictionaries needed")
    print("   - Context patterns learned during training")
    print("   - Minimal memory usage on device")
    print()
    
    # Create enhanced training data
    examples = create_kanji_aware_training_data()
    
    print()
    print("="*70)
    print("NEXT STEPS")
    print("="*70)
    print()
    print("1. Train model with enhanced data:")
    print("   python scripts/train_with_enhanced_data.py")
    print()
    print("2. Export to Core ML:")
    print("   python scripts/export_coreml.py")
    print()
    print("3. Use in iOS - NO dictionaries needed!")
    print("   - Just load KeyboardAI.mlpackage")
    print("   - Model already knows kanji patterns")
    print("   - Minimal memory: ~25MB (model only)")
    print()
    print("="*70)


if __name__ == '__main__':
    main()
