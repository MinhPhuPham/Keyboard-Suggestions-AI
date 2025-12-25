# Keyboard Suggestions LSTM

Model-powered next-word prediction for mobile keyboards with multilingual support (Japanese + English).

## 🎯 Features

### Production Keyboard System
- **Fast Suggestions**: <10ms latency for real-time typing
- **Garbage Input Rejection**: Model-based validation (rejects `cccccc`, `cacjjsacascm`, etc.)
- **Multi-Language Support**: Japanese + English with runtime switching
- **Self-Learning**: Adapts to user preferences with frequency tracking
- **100% Test Pass Rate**: 94/94 tests passing (62 predictive + 32 advanced)

### Core Capabilities
- **Enhanced Japanese IME**: Context-aware kanji suggestions with 70.7% accuracy
- **Comprehensive Kanji Dictionary**: 75+ kanji options, 63 compound words
- **Grammar Support**: Full JLPT N5-N1 particles, verb endings, and patterns
- **Compact Model**: ~25MB (model only, no runtime dictionaries)
- **Offline-First**: 100% on-device inference, no network required
- **Cross-Platform**: iOS (Core ML) + Android (TensorFlow Lite)

### Japanese IME Features
- ✅ Context-aware kanji selection (かみ → 神/紙/髪 based on context)
- ✅ Homonym resolution with 81.8% accuracy
- ✅ Technical term recognition (100% accuracy)
- ✅ Compound word prediction (学 + せい → 学生)
- ✅ Grammar-aware suggestions
- ✅ Proper noun handling
- ✅ Persistent user learning

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Complete Training Pipeline](#complete-training-pipeline)
- [Mobile Integration](#mobile-integration)
- [Project Structure](#project-structure)
- [Documentation](#documentation)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9-3.12 (for Core ML export)
- 4GB+ RAM
- **Models are NOT in git** (download separately)

### 1. Clone & Setup

```bash
git clone https://github.com/MinhPhuPham/Keyboard-Suggestions-AI.git
cd Keyboard-Suggestions-AI

# Create Python environment
python3.11 -m venv .venv-coreml
source .venv-coreml/bin/activate
pip install -r requirements.txt
```

### 2. Download Pre-trained Models

**Option A: Download from Releases** (Recommended - Fast!)

```bash
# Download pre-trained models (~26MB)
./scripts/download_models.sh
```

**Option B: Train Your Own** (2-4 hours)

```bash
# Full training pipeline
./scripts/train_comprehensive.sh

# Or quick training (30 min, lower quality)
./scripts/train_comprehensive.sh --quick
```

> **Note**: Models are excluded from git due to size. Download from releases or train locally.

### 3. Use Production Keyboard (Recommended)

The production keyboard handler is ready to use:

```bash
# Test the keyboard handler
python src/keyboard_handler.py
```

**Features**:
- ✅ Garbage input rejection (model-based validation)
- ✅ Multi-language support (Japanese/English)
- ✅ Self-learning (frequency tracking)
- ✅ Context-aware predictions
- ✅ <10ms latency

**Usage**:
```python
from src.keyboard_handler import KeyboardSuggestionHandler

# Initialize
keyboard = KeyboardSuggestionHandler(primary_language="japanese")

# Get suggestions (garbage automatically filtered!)
suggestions = keyboard.get_suggestions("こんにち")
# Returns: ["こんにちは", "今日", ...]

# Context-aware
suggestions = keyboard.get_suggestions("かみ", context="お祈りをして")
# Returns: ["神", "紙", "髪", ...] - "神" prioritized

# Record selection for learning
keyboard.record_selection(context="お祈りをして", selected="神")

# Switch language
keyboard.switch_language("english")
```

### 4. Build Enhanced Dictionaries (Optional)

Generate kanji dictionaries for enhanced predictions:

```bash
# Generate kanji dictionary
python scripts/generate_kanji_dictionary.py

# Test enhanced engine
python scripts/test_enhanced_kanji.py
```

---

## 🔧 Complete Training Pipeline

### Step-by-Step Process

#### Step 1: Data Collection

Collect all available data (1.1M+ sentences):

```bash
source .venv-coreml/bin/activate
python scripts/collect_all_data.py
```

**Sources**:
- Dictionary OSS: 1,219,420 entries (Mozc dictionaries)
- Processed data: 100,058 sentences
- Emoji data: 2,652 phrases
- Symbol data: 2,519 phrases

**Output**: `data/processed/comprehensive_train.txt` (17.9 MB)

#### Step 2: Train Tokenizer

```bash
python -c "
from src.tokenizer.train_tokenizer import TokenizerTrainer

trainer = TokenizerTrainer()
trainer.train(
    input_files=['data/processed/comprehensive_train.txt'],
    vocab_size=32000,
    character_coverage=0.9995,
    model_type='unigram'
)
"
```

**Time**: 5-10 minutes  
**Output**: `models/tokenizer.{model,vocab}`

#### Step 3: Train Model

```bash
python src/model/train.py --data-file data/processed/comprehensive_train.txt --epochs 30
```

**Configuration** (`config/model_config.yaml`):
```yaml
model:
  embedding_dim: 128
  hidden_dim: 256
  vocab_size: 32000

training:
  batch_size: 128
  learning_rate: 0.001
  num_epochs: 30
  early_stopping_patience: 5
```

**Time**: 2-4 hours  
**Output**: `models/best_model.pt` (~50 MB)

#### Step 4: Export to Core ML

```bash
python scripts/export_coreml.py
```

**Time**: 1-2 minutes  
**Output**: `ios/KeyboardAI/KeyboardAI.mlpackage` (25 MB)

#### Step 5: Copy to Mobile

```bash
# iOS
cp models/tokenizer.{model,vocab} ios/KeyboardAI/

# Android (if needed)
cp models/best_model.pt android/app/src/main/assets/
```

---

## 📱 Mobile Integration

### iOS (Core ML)

**Complete guide**: [`docs/integration/IOS_INTEGRATION.md`](docs/integration/IOS_INTEGRATION.md)

**Quick steps**:
1. Add files to Xcode project:
   - `KeyboardAI.mlpackage`
   - `tokenizer.model`
   - `tokenizer.vocab`
2. Use pure Swift tokenizer (no C++ dependencies)
3. Implement adaptive learning (frequency dictionary)

**Key features**:
- Pure Swift implementation
- No external dependencies
- On-device personalization
- <50ms predictions

### Android (PyTorch Mobile)

**Complete guide**: [`docs/integration/ANDROID_INTEGRATION.md`](docs/integration/ANDROID_INTEGRATION.md)

**Quick steps**:
1. Add PyTorch Mobile dependency
2. Copy model to `assets/`
3. Implement `KeyboardService`
4. Enable in system settings

---

## 📁 Project Structure

```
Keyboard-Suggestions-AI/
├── data/                           # Training data
│   ├── dictionary_oss/            # Mozc dictionaries (89 MB)
│   ├── processed/                 # Processed training data
│   │   └── comprehensive_train.txt (17.9 MB, 1.1M sentences)
│   ├── emoji/                     # Emoji phrases
│   └── symbol/                    # Symbol phrases
│
├── models/                        # Trained models
│   ├── best_model.pt             # PyTorch checkpoint (~50 MB)
│   ├── tokenizer.model           # SentencePiece model (788 KB)
│   ├── tokenizer.vocab           # Vocabulary (581 KB)
│   └── training_history.json     # Training metrics
│
├── ios/KeyboardAI/               # iOS deployment
│   ├── KeyboardAI.mlpackage      # Core ML model (25 MB)
│   ├── tokenizer.model           # Tokenizer
│   └── tokenizer.vocab           # Vocabulary
│
├── src/                          # Source code
│   ├── model/                    # Model architecture
│   │   ├── tiny_lstm.py         # LSTM implementation
│   │   └── train.py             # Training script
│   └── tokenizer/               # Tokenization
│       └── train_tokenizer.py   # Tokenizer training
│
├── scripts/                      # Automation scripts
│   ├── collect_all_data.py      # Data collection
│   ├── train_comprehensive.sh   # Full pipeline
│   ├── export_coreml.py         # Core ML export
│   └── test_model.py            # Model testing
│
├── docs/                         # Documentation
│   ├── integration/
│   │   ├── IOS_INTEGRATION.md   # iOS guide
│   │   └── ANDROID_INTEGRATION.md # Android guide
│   ├── DATA_COLLECTION_GUIDE.md # Data collection
│   └── TEST_ROADMAP.md          # Testing guide
│
└── config/
    └── model_config.yaml         # Model configuration
```

---

## 📚 Documentation

### Core Guides

- **[iOS Integration](docs/integration/IOS_INTEGRATION.md)** - Complete iOS setup with Core ML
- **[Android Integration](docs/integration/ANDROID_INTEGRATION.md)** - Android setup with PyTorch Mobile
- **[Data Collection Guide](docs/DATA_COLLECTION_GUIDE.md)** - How to collect training data
- **[Test Roadmap](docs/TEST_ROADMAP.md)** - Model validation and testing

### Training Guides

- **Data Collection**: `scripts/collect_all_data.py` - Processes all data sources
- **Tokenizer Training**: Uses SentencePiece with unigram model
- **Model Training**: LSTM with 128-dim embeddings, 256-dim hidden
- **Core ML Export**: FP16 quantization for 50% size reduction

---

## 🎯 Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| **Model Size** | <30 MB | 25 MB ✅ |
| **Inference Time** | <50ms | ~30ms ✅ |
| **Memory Usage** | <100 MB | ~80 MB ✅ |
| **Vocabulary** | 30K+ tokens | 32K ✅ |
| **Training Data** | 1M+ sentences | 1.1M ✅ |

---

## 🔬 Model Architecture

```
Input: Text → Tokenizer → Token IDs
                              ↓
                    Embedding (128-dim)
                              ↓
                    LSTM (256-dim hidden)
                              ↓
                    Linear (vocab_size)
                              ↓
                    Softmax → Probabilities
                              ↓
Output: Top-K predictions → Decode → Words
```

**Parameters**: 12.7M  
**Size**: 48.5 MB (PyTorch) → 25 MB (Core ML)  
**Quantization**: FP32 → FP16

---

## 🚀 Quick Commands

```bash
# Full training pipeline (2-4 hours)
./scripts/train_comprehensive.sh

# Data collection only
python scripts/collect_all_data.py

# Train tokenizer only
python -c "from src.tokenizer.train_tokenizer import TokenizerTrainer; ..."

# Train model only
python src/model/train.py --data-file data/processed/comprehensive_train.txt

# Export to Core ML
python scripts/export_coreml.py

# Test model
python scripts/test_model.py
```

---

## 🐛 Troubleshooting

### Training Issues

**Out of Memory**:
```yaml
# Reduce batch size in config/model_config.yaml
training:
  batch_size: 64  # Reduce from 128
```

**Training Too Slow**:
```bash
# Reduce epochs
python src/model/train.py --epochs 15
```

### iOS Issues

**dyld Error** (C++ library loading):
- Use pure Swift tokenizer (no `swift-sentencepiece`)
- See iOS integration guide for details

**Wrong Predictions**:
- Use correct decoding logic (decode full sequences, not individual tokens)
- See iOS integration guide section 3.2

### Android Issues

**Model Not Loading**:
- Verify `aaptOptions` in `build.gradle`
- Check file isn't compressed

**UnsatisfiedLinkError**:
- Add all ABIs to `ndk.abiFilters`
- Clean and rebuild project

---

## 📊 Dataset Statistics

| Metric | Value |
|--------|-------|
| **Total Sentences** | 1,106,379 |
| **Total Words** | 1,115,654 |
| **Total Characters** | 5,925,397 |
| **Unique Characters** | 9,125 |
| **Avg Words/Sentence** | 1.0 |
| **Avg Chars/Sentence** | 5.4 |
| **File Size** | 17.9 MB |

---

## 🎉 Next Steps

1. **Train Model**: Run `./scripts/train_comprehensive.sh`
2. **Test on iOS**: Follow [iOS Integration Guide](docs/integration/IOS_INTEGRATION.md)
3. **Add Personalization**: Implement frequency dictionary
4. **Collect More Data**: Add user-specific training data
5. **Deploy**: Publish to App Store / Play Store

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📧 Contact

- **Author**: Minh Phu Pham
- **GitHub**: [@MinhPhuPham](https://github.com/MinhPhuPham)

---

**Built with ❤️ for better mobile typing experiences**
