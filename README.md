# Keyboard Suggestions AI

AI-powered next-word prediction for mobile keyboards with Japanese support.

## Features

- **Japanese Support**: Trained on 1M+ Japanese words from Mozc dictionary
- **Large Vocabulary**: 32,000 tokens for comprehensive Japanese coverage
- **Compact Model**: 25MB Core ML model (FP16 precision)
- **Custom Dictionary**: Hot-reload user abbreviations (<50ms)
- **Language Rules**: Configurable formality, slang, emoji frequency
- **No-Mean Filter**: Blocks spam and keyboard mashing
- **Offline**: 100% on-device, no network required
- **Cross-Platform**: iOS (Core ML) + Android (TFLite) ready

---

## Quick Start

### 1. Install Dependencies

```bash
# Clone repository
git clone https://github.com/MinhPhuPham/Keyboard-Suggestions-AI.git
cd Keyboard-Suggestions-AI

# Install core dependencies
pip install -r requirements.txt
```

**Note**: Core ML export requires Python 3.9-3.12. Create separate environment:
```bash
python3.11 -m venv .venv-coreml
source .venv-coreml/bin/activate
pip install coremltools torch sentencepiece pyyaml
```

### 2. Train Model

```bash
# Extract Japanese training data (100K sentences from 1M+ words)
python scripts/extract_japanese_data.py --num-sentences 100000

# Train tokenizer (32K vocab)
python -c "
from src.tokenizer.train_tokenizer import TokenizerTrainer
trainer = TokenizerTrainer()
trainer.train(
    input_files=['data/processed/japanese_train_large.txt'],
    vocab_size=32000,
    character_coverage=0.9995,
    model_type='unigram'
)
"

# Train model
python src/model/train.py --epochs 50

# Export to Core ML
source .venv-coreml/bin/activate
python scripts/export_coreml.py --model models/best_model.pt
```

**Output**:
- `models/tokenizer.model` (~788 KB, 32K vocab)
- `models/best_model.pt` (trained model, ~146 MB)
- `ios/KeyboardAI/KeyboardAI.mlpackage` (~25 MB Core ML)

### 3. Test Predictions

```bash
python src/inference/prediction_engine.py
```

---

## Automated Build (One Command)

### Complete Pipeline

Build everything from scratch to iOS/Android packages in one command:

```bash
./build-package-complete.sh
```

**What it does**:
1. ✅ Installs dependencies
2. ✅ Extracts Japanese training data (100K sentences)
3. ✅ Trains tokenizer (32K vocab)
4. ✅ Trains model (50 epochs)
5. ✅ Exports to Core ML
6. ✅ Copies tokenizer to iOS package
7. ✅ Creates iOS/Android packages

**Output**:
- `ios/KeyboardAI/KeyboardAI.mlpackage` (~25 MB)
- `ios/KeyboardAI/tokenizer.model` (~788 KB)
- `ios/KeyboardAI/tokenizer.vocab` (~581 KB)

### Quick Build Options

```bash
# Quick test build (5 epochs, ~1 minute)
./build-package-complete.sh --quick

# Skip dependency installation
./build-package-complete.sh --skip-install

# Skip training (use existing model)
./build-package-complete.sh --skip-training

# Custom epoch count
./build-package-complete.sh --epochs 100

# Combine options
./build-package-complete.sh --quick --skip-install
```

### Package Contents

iOS package includes:
- `KeyboardAI.mlpackage` - Core ML model (~25 MB)
- `tokenizer.model` - SentencePiece tokenizer (~788 KB)
- `tokenizer.vocab` - Vocabulary file (~581 KB)
- `language_rules.yaml` - EN/JA language rules
- `custom_dictionary.json` - Custom abbreviations
- `model_info.json` - Model metadata
- `README.md` - Integration instructions

---

## Project Structure

```
├── src/
│   ├── model/          # TinyLSTM architecture & training
│   ├── tokenizer/      # SentencePiece training
│   ├── dictionary/     # Custom dictionary with prefix trie
│   ├── rules/          # Language rules & no-mean filter
│   ├── inference/      # Prediction engine
│   └── utils/          # Data prep, config, export
├── config/
│   ├── model_config.yaml        # Model hyperparameters
│   ├── language_rules.yaml      # EN/JA language rules
│   └── custom_dictionary.json   # User abbreviations
├── data/
│   ├── raw/            # Raw training data
│   └── processed/      # Cleaned & combined data
├── models/             # Trained models
├── test-data/          # Test examples (30+ cases)
├── scripts/            # Build & export scripts
└── docs/               # Integration guides

```

---

## Training Your Own Model

### Japanese Data (Included!)

The project includes Japanese dictionary data from Mozc:

```bash
# Extract training data from included dictionaries
python scripts/extract_japanese_data.py --num-sentences 100000
```

**What it extracts**:
- 1,033,624 unique words from `data/dictionary_oss/`
- 6,465 kanji mappings from `data/single_kanji/`
- 439 emoticons from `data/emoticon/`
- 1,909 emoji mappings from `data/emoji/`

**Output**: 100,000 natural Japanese sentences in `data/processed/japanese_train_large.txt`

### Collect Additional Data

See [`DATA_COLLECTION_GUIDE.md`](DATA_COLLECTION_GUIDE.md) for detailed instructions.

**Minimum Requirements**:
- English: 1,000+ sentences
- Japanese: Already included! (100K sentences)
- Format: One sentence per line, UTF-8

**Example**:
```
data/raw/english_casual.txt:
I'm going to the store
wanna grab coffee?
that's so cool!
...
```

### Clean & Train

```bash
# Extract Japanese data
python scripts/extract_japanese_data.py

# Train tokenizer with large vocab
python -c "
from src.tokenizer.train_tokenizer import TokenizerTrainer
trainer = TokenizerTrainer()
trainer.train(
    input_files=['data/processed/japanese_train_large.txt'],
    vocab_size=32000,
    character_coverage=0.9995
)
"

# Train model
python src/model/train.py --epochs 50
```

---

## Mobile Integration

### Package Files

After running `./build-package-complete.sh`, you'll have:
- `ios/KeyboardAI-iOS-Package.zip` (~572 KB)
- `android/KeyboardAI-Android-Package.zip` (~572 KB)

Each package contains:
- `tiny_lstm.pt` - TorchScript model
- `tokenizer.model` + `.vocab` - SentencePiece tokenizer
- `language_rules.yaml` - Language rules
- `custom_dictionary.json` - Custom dictionary
- `model_info.json` - Model metadata

---

### iOS Integration

**Framework**: Core ML (Native iOS)

**Key Steps**:
1. Export to Core ML: `python scripts/export_coreml.py`
2. Add `.mlpackage` to Xcode project
3. Use pure Swift (no C++ needed!)
4. Integrate into keyboard extension

**Complete Guide**: [`docs/integration/IOS_INTEGRATION.md`](docs/integration/IOS_INTEGRATION.md)

**Includes**:
- ✅ Core ML export instructions
- ✅ Pure Swift implementation (no Objective-C++)
- ✅ Keyboard extension integration
- ✅ Performance optimization
- ✅ Troubleshooting

**Example Code**:
```swift
// Load Core ML model
let model = try KeyboardAI(contentsOf: modelURL)

// Run prediction
let output = try model.prediction(input_ids: inputArray)
```

**Advantages over PyTorch Mobile**:
- ✅ 40% smaller size (~300 KB vs ~500 KB)
- ✅ No C++17 complexity
- ✅ Native iOS optimization
- ✅ Better battery efficiency
- ✅ Simple Swift API

---

### Android Integration

**Framework**: PyTorch Mobile for Android

**Key Steps**:
1. Add Gradle dependency: `org.pytorch:pytorch_android_lite:1.13.1`
2. Copy model to `assets/` folder
3. Load with `LiteModuleLoader.load()`
4. Integrate into Input Method Service

**Complete Guide**: [`docs/integration/ANDROID_INTEGRATION.md`](docs/integration/ANDROID_INTEGRATION.md)

**Includes**:
- ✅ Android Studio setup
- ✅ Gradle configuration
- ✅ Kotlin/Java implementation
- ✅ Keyboard service code
- ✅ Layout XML and manifest
- ✅ Performance optimization

**Example Code**:
```kotlin
// Load model
val module = LiteModuleLoader.load(modelPath)

// Run prediction
val outputTensor = module.forward(IValue.from(inputTensor))
```

---

### Integration Checklist

**Before Integration**:
- [ ] Extract package zip file
- [ ] Read integration guide for your platform
- [ ] Install required dependencies

**iOS**:
- [ ] Add files to Xcode project
- [ ] Install CocoaPods (`pod install`)
- [ ] Create Objective-C++ bridge
- [ ] Implement Swift wrapper
- [ ] Test on device

**Android**:
- [ ] Add files to `assets/` folder
- [ ] Update `build.gradle`
- [ ] Implement Kotlin/Java wrapper
- [ ] Create keyboard service
- [ ] Test on device

**After Integration**:
- [ ] Measure prediction latency
- [ ] Monitor memory usage
- [ ] Test with real users
- [ ] Report performance metrics

---

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Prediction Latency | < 50ms | Time from input to suggestion |
| Memory Usage | < 30MB | Total keyboard memory |
| Model Load Time | < 500ms | App launch to ready |
| Package Size | < 5MB | Total added to app |

**Current Demo Model**:
- Package size: ~700 KB ✅
- Model size: ~512 KB ✅
- Tokenizer size: ~256 KB ✅

---

### Troubleshooting

**iOS - Model Not Loading**:
- Check file is in keyboard extension target
- Verify CocoaPods installation
- See iOS integration guide

**Android - UnsatisfiedLinkError**:
- Add all ABIs to `ndk.abiFilters`
- Check PyTorch version compatibility
- See Android integration guide

**Both - High Memory Usage**:
- Implement prediction caching
- Use lazy loading
- Release resources when not in use

---

### Next Steps

1. **Extract package** for your platform
2. **Follow integration guide** step-by-step
3. **Test on device** and measure performance
4. **Report metrics** for optimization
5. **Collect real data** and retrain for production

---

## Configuration

### Model Config (`config/model_config.yaml`)

```yaml
model:
  vocab_size: 100      # Match tokenizer vocab
  embedding_dim: 64
  hidden_dim: 128
  num_layers: 1
  dropout: 0.2

training:
  batch_size: 128
  learning_rate: 0.001
  num_epochs: 50
  early_stopping_patience: 5
```

### Language Rules (`config/language_rules.yaml`)

```yaml
languages:
  en:
    formality: "casual"
    emoji_frequency: "high"
    boost_tokens: ["gonna", "wanna", "lol"]
    suppress_tokens: ["whom", "whomst"]
    
  ja:
    formality: "polite"
    emoji_frequency: "low"
    boost_tokens: ["です", "ます"]
    suppress_tokens: ["だ", "じゃん"]
```

### Custom Dictionary (`config/custom_dictionary.json`)

```json
{
  "entries": {
    "ty": {"value": "thank you", "priority": 1},
    "brb": {"value": "be right back", "priority": 1},
    "omw": {"value": "on my way", "priority": 1}
  }
}
```

---

## Performance Targets

| Metric | Target | Demo Model |
|--------|--------|------------|
| Model Size | < 5 MB | ~0.7 MB ✅ |
| Prediction Latency | < 50 ms | TBD (device testing) |
| Memory Usage | < 30 MB | TBD (device testing) |
| Accuracy (Top-3) | > 70% | TBD (needs real data) |

---

## Development Workflow

### 1. Setup
```bash
pip install -r requirements.txt
```

### 2. Develop
```bash
# Run tests
pytest tests/

# Check code
python src/dictionary/custom_dict.py
python src/rules/rule_engine.py
```

### 3. Train
```bash
# Full pipeline
python src/utils/data_prep.py
python src/tokenizer/train_tokenizer.py
python src/model/train.py
python src/utils/export_model.py
```

### 4. Deploy
```bash
# For iOS/Android (requires Python 3.11)
# See docs/MOBILE_PACKAGES.md
```

---

## Troubleshooting

### Python 3.13 Compatibility

**Issue**: `tensorflow` and `coremltools` don't support Python 3.13

**Solutions**:
1. Use TorchScript export (already working)
2. Create Python 3.11 environment for mobile export only
3. Use Docker with Python 3.11

### Small Dataset Warning

**Issue**: Demo model trained on only 29 samples

**Impact**: Poor generalization, low accuracy

**Solution**: Collect 10,000+ real sentences per language

### Japanese Tokenization

**Issue**: Japanese samples showing as invalid

**Solution**: Ensure UTF-8 encoding, check text normalization

---

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

---

## License

MIT License - See LICENSE file

---

## Support

- **Issues**: GitHub Issues
- **Docs**: `/docs` folder
- **Examples**: `/test-data` folder

---

## Roadmap

- [x] Phase 1-6: Core implementation
- [ ] Phase 7: iOS integration
- [ ] Phase 8: Android integration  
- [ ] Phase 9: Testing & validation
- [ ] Phase 10: App store release

See [`TRAINING_SUMMARY.md`](TRAINING_SUMMARY.md) for detailed execution log.
