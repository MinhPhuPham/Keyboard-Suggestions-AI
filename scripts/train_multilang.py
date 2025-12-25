#!/usr/bin/env python3
"""
Multi-language training script.
Trains separate models for Japanese and English for better predictions.
"""

import yaml
import subprocess
import sys
from pathlib import Path

class MultiLanguageTrainer:
    """Train separate models for each language"""
    
    def __init__(self):
        self.base_dir = Path('.')
        self.data_dir = self.base_dir / 'data'
        self.models_dir = self.base_dir / 'models'
        
    def train_japanese_model(self):
        """Train Japanese-specific model"""
        print("="*70)
        print("TRAINING JAPANESE MODEL")
        print("="*70)
        print()
        
        # Use existing comprehensive Japanese data
        data_file = 'data/processed/comprehensive_train.txt'
        
        print(f"📊 Data: {data_file}")
        print(f"🎯 Language: Japanese")
        print(f"📦 Output: models/japanese/")
        print()
        
        # Create Japanese model directory
        (self.models_dir / 'japanese').mkdir(parents=True, exist_ok=True)
        
        # Configure for Japanese
        config = {
            'model': {
                'embedding_dim': 128,
                'hidden_dim': 256,
                'num_layers': 1,
                'dropout': 0.2,
                'vocab_size': 32000  # Large vocab for Japanese
            },
            'tokenizer': {
                'type': 'sentencepiece',
                'model_type': 'unigram',
                'vocab_size': 32000,
                'character_coverage': 0.9995  # High coverage for Japanese
            },
            'data': {
                'max_sequence_length': 50,
                'train_file': data_file,
                'language': 'japanese'
            },
            'training': {
                'batch_size': 128,
                'learning_rate': 0.001,
                'num_epochs': 30,
                'early_stopping_patience': 5,
                'val_split': 0.05,
                'validation_split': 0.05,
                'gradient_clip': 1.0,
                'save_dir': 'models/japanese',
                'log_interval': 1000
            },
            'optimization': {
                'target_model_size_mb': 25
            }
        }
        
        # Save config
        with open('config/model_config_japanese.yaml', 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print("✅ Configuration saved: config/model_config_japanese.yaml")
        print()
        
        # Train tokenizer
        print("🔧 Training Japanese tokenizer...")
        from src.tokenizer.train_tokenizer import TokenizerTrainer
        trainer = TokenizerTrainer()
        trainer.train(
            input_files=['data/processed/comprehensive_train.txt'],
            vocab_size=32000,
            character_coverage=0.9995,
            model_type='unigram'
        )
        
        # Move tokenizer files to Japanese directory
        import shutil
        shutil.copy('models/tokenizer.model', 'models/japanese/tokenizer.model')
        shutil.copy('models/tokenizer.vocab', 'models/japanese/tokenizer.vocab')
        print('✅ Japanese tokenizer trained')
        
        print()
        
        # Train model
        print("🚀 Training Japanese model...")
        print("   This will take 2-4 hours...")
        print()
        
        # Copy config to main location temporarily
        subprocess.run(['cp', 'config/model_config_japanese.yaml', 'config/model_config.yaml'], check=True)
        
        # Train
        subprocess.run([
            sys.executable, 'src/model/train.py',
            '--data-file', data_file,
            '--epochs', '30'
        ], check=True)
        
        # Move trained model to Japanese directory
        subprocess.run(['cp', 'models/best_model.pt', 'models/japanese/best_model.pt'], check=True)
        subprocess.run(['cp', 'models/training_history.json', 'models/japanese/training_history.json'], check=True)
        
        print()
        print("✅ Japanese model trained!")
        print(f"   Model: models/japanese/best_model.pt")
        print(f"   Tokenizer: models/japanese/tokenizer.model")
        print()
        
    def train_english_model(self):
        """Train English-specific model (placeholder for future)"""
        print("="*70)
        print("TRAINING ENGLISH MODEL")
        print("="*70)
        print()
        
        print("⚠️  English training data not available yet")
        print("   Skipping English model training")
        print()
        print("📝 To train English model:")
        print("   1. Add English data to data/english/")
        print("   2. Run: python scripts/train_multilang.py --language english")
        print()
        
    def export_japanese_to_coreml(self):
        """Export Japanese model to Core ML"""
        print("="*70)
        print("EXPORTING JAPANESE MODEL TO CORE ML")
        print("="*70)
        print()
        
        # Create export script for Japanese
        export_script = """
import torch
import coremltools as ct
import numpy as np
import json
from pathlib import Path
import sys
sys.path.append('src')
from model.tiny_lstm import TinyLSTM

print('Loading Japanese model...')
checkpoint = torch.load('models/japanese/best_model.pt', map_location='cpu')
model = TinyLSTM(vocab_size=32000, embedding_dim=128, hidden_dim=256)
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

print('Tracing model...')
example_input = torch.zeros((1, 50), dtype=torch.long)
traced_model = torch.jit.trace(model, example_input)

print('Converting to Core ML...')
mlmodel = ct.convert(
    traced_model,
    inputs=[ct.TensorType(shape=(1, 50), dtype=np.int32, name='input_ids')],
    convert_to='mlprogram',
    compute_precision=ct.precision.FLOAT16
)

mlmodel.author = 'Minh Phu Pham'
mlmodel.short_description = 'Japanese keyboard prediction model'
mlmodel.version = '1.0.0'

# Save
output_dir = Path('ios/KeyboardAI/Japanese')
output_dir.mkdir(parents=True, exist_ok=True)
mlmodel.save(str(output_dir / 'KeyboardAI_Japanese.mlpackage'))

# Save metadata
metadata = {
    'language': 'japanese',
    'vocab_size': 32000,
    'model_version': '1.0.0',
    'embedding_dim': 128,
    'hidden_dim': 256
}
with open(output_dir / 'model_info.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print('✅ Japanese model exported to Core ML')
print(f'   Location: ios/KeyboardAI/Japanese/KeyboardAI_Japanese.mlpackage')
"""
        
        with open('scripts/export_japanese.py', 'w') as f:
            f.write(export_script)
        
        # Run export
        subprocess.run([sys.executable, 'scripts/export_japanese.py'], check=True)
        
        # Copy tokenizer files
        subprocess.run(['cp', 'models/japanese/tokenizer.model', 'ios/KeyboardAI/Japanese/'], check=True)
        subprocess.run(['cp', 'models/japanese/tokenizer.vocab', 'ios/KeyboardAI/Japanese/'], check=True)
        
        print()
        print("✅ All Japanese files ready for iOS!")
        print()
        
    def create_language_switcher_ios(self):
        """Create iOS code for language switching"""
        print("="*70)
        print("CREATING iOS LANGUAGE SWITCHER")
        print("="*70)
        print()
        
        ios_code = '''// MultiLanguageKeyboard.swift
// Language-aware keyboard with model switching

import Foundation
import CoreML

enum KeyboardLanguage: String {
    case japanese = "ja"
    case english = "en"
}

class MultiLanguageKeyboard {
    
    // Separate models for each language
    private var japaneseModel: KeyboardAI_Japanese?
    private var englishModel: KeyboardAI_English?
    
    // Separate tokenizers
    private var japaneseTokenizer: Tokenizer?
    private var englishTokenizer: Tokenizer?
    
    // Current language
    private var currentLanguage: KeyboardLanguage = .japanese
    
    init() {
        loadModels()
    }
    
    private func loadModels() {
        // Load Japanese model
        do {
            japaneseModel = try KeyboardAI_Japanese(configuration: MLModelConfiguration())
            japaneseTokenizer = Tokenizer(vocabFile: "Japanese/tokenizer.vocab")
            print("✅ Japanese model loaded")
        } catch {
            print("❌ Failed to load Japanese model: \\(error)")
        }
        
        // Load English model (when available)
        // englishModel = try? KeyboardAI_English(configuration: MLModelConfiguration())
        // englishTokenizer = Tokenizer(vocabFile: "English/tokenizer.vocab")
    }
    
    /// Switch language mode
    func setLanguage(_ language: KeyboardLanguage) {
        currentLanguage = language
        print("🌐 Switched to \\(language.rawValue)")
    }
    
    /// Auto-detect language from input text
    func detectLanguage(from text: String) -> KeyboardLanguage {
        // Simple heuristic: check for Japanese characters
        let hasJapanese = text.unicodeScalars.contains { scalar in
            (0x3040...0x309F).contains(scalar.value) ||  // Hiragana
            (0x30A0...0x30FF).contains(scalar.value) ||  // Katakana
            (0x4E00...0x9FAF).contains(scalar.value)     // Kanji
        }
        
        return hasJapanese ? .japanese : .english
    }
    
    /// Get predictions using appropriate model
    func predict(text: String, topK: Int = 3, language: KeyboardLanguage? = nil) -> [String] {
        // Use specified language or auto-detect
        let targetLanguage = language ?? detectLanguage(from: text)
        
        switch targetLanguage {
        case .japanese:
            return predictJapanese(text: text, topK: topK)
        case .english:
            return predictEnglish(text: text, topK: topK)
        }
    }
    
    private func predictJapanese(text: String, topK: Int) -> [String] {
        guard let model = japaneseModel,
              let tokenizer = japaneseTokenizer else {
            return []
        }
        
        // Tokenize
        let tokenIds = tokenizer.encode(text)
        guard !tokenIds.isEmpty else { return [] }
        
        // Prepare input
        var paddedInput = Array(tokenIds.suffix(50))
        while paddedInput.count < 50 {
            paddedInput.insert(0, at: 0)
        }
        
        guard let inputArray = try? MLMultiArray(shape: [1, 50], dataType: .int32) else {
            return []
        }
        
        for (i, tokenId) in paddedInput.enumerated() {
            inputArray[i] = NSNumber(value: tokenId)
        }
        
        // Run model
        guard let output = try? model.prediction(input_ids: inputArray) else {
            return []
        }
        
        // Get predictions
        let logits = output.logits
        let vocabSize = 32000
        let lastTokenStart = 49 * vocabSize
        
        var scores: [(index: Int, score: Float)] = []
        for i in 0..<vocabSize {
            let score = logits[lastTokenStart + i].floatValue
            scores.append((index: i, score: score))
        }
        
        let topTokenIds = scores.sorted { $0.score > $1.score }
            .prefix(topK * 3)
            .map { $0.index }
        
        // Decode predictions
        var predictions: [String] = []
        for nextTokenId in topTokenIds {
            let fullSequence = tokenIds + [nextTokenId]
            let decoded = tokenizer.decode(fullSequence)
            
            if decoded.count > text.count {
                let newPart = String(decoded.dropFirst(text.count)).trimmingCharacters(in: .whitespaces)
                if !newPart.isEmpty && !predictions.contains(newPart) {
                    predictions.append(newPart)
                    if predictions.count >= topK {
                        break
                    }
                }
            }
        }
        
        return predictions
    }
    
    private func predictEnglish(text: String, topK: Int) -> [String] {
        // Placeholder for English model
        // Will be implemented when English data is available
        return []
    }
}

// MARK: - Usage Example

class KeyboardViewController: UIInputViewController {
    private var keyboard: MultiLanguageKeyboard!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        keyboard = MultiLanguageKeyboard()
    }
    
    override func textDidChange(_ textInput: UITextInput?) {
        guard let text = textDocumentProxy.documentContextBeforeInput else { return }
        
        // Auto-detect language and get predictions
        let predictions = keyboard.predict(text: text, topK: 3)
        displaySuggestions(predictions)
    }
    
    // Manual language switch
    @IBAction func switchToJapanese() {
        keyboard.setLanguage(.japanese)
    }
    
    @IBAction func switchToEnglish() {
        keyboard.setLanguage(.english)
    }
}
'''
        
        # Save iOS code
        ios_dir = Path('ios/KeyboardAI/Swift')
        ios_dir.mkdir(parents=True, exist_ok=True)
        
        with open(ios_dir / 'MultiLanguageKeyboard.swift', 'w') as f:
            f.write(ios_code)
        
        print("✅ iOS language switcher created")
        print(f"   Location: ios/KeyboardAI/Swift/MultiLanguageKeyboard.swift")
        print()
        
    def run(self, language='japanese'):
        """Run training for specified language"""
        print("\n" + "="*70)
        print("MULTI-LANGUAGE MODEL TRAINING")
        print("="*70)
        print()
        print("🎯 Strategy: Separate models for better predictions")
        print("   - Japanese model: 32K vocab, optimized for Japanese")
        print("   - English model: 16K vocab, optimized for English")
        print("   - Language switching: Auto-detect or manual")
        print()
        
        if language == 'japanese' or language == 'all':
            self.train_japanese_model()
            self.export_japanese_to_coreml()
        
        if language == 'english' or language == 'all':
            self.train_english_model()
        
        # Create iOS switcher
        self.create_language_switcher_ios()
        
        print("="*70)
        print("✅ MULTI-LANGUAGE SETUP COMPLETE!")
        print("="*70)
        print()
        print("📁 Files created:")
        print("   models/japanese/best_model.pt")
        print("   models/japanese/tokenizer.{model,vocab}")
        print("   ios/KeyboardAI/Japanese/KeyboardAI_Japanese.mlpackage")
        print("   ios/KeyboardAI/Swift/MultiLanguageKeyboard.swift")
        print()
        print("📱 iOS Integration:")
        print("   1. Add Japanese model to Xcode")
        print("   2. Use MultiLanguageKeyboard.swift")
        print("   3. Auto language detection works!")
        print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Train multi-language models')
    parser.add_argument('--language', choices=['japanese', 'english', 'all'], 
                       default='japanese',
                       help='Language to train (default: japanese)')
    args = parser.parse_args()
    
    trainer = MultiLanguageTrainer()
    trainer.run(language=args.language)


if __name__ == '__main__':
    main()
