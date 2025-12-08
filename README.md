# Keyboard Suggestions AI

On-device multilingual next-word prediction for iOS/Android keyboard extensions.

## Features

- 🚀 **Tiny Model**: <5 MB total size (model + tokenizer + rules)
- 🌍 **Multilingual**: English + Japanese with extensible architecture
- ⚡ **Fast**: <50ms prediction latency
- 📝 **Custom Dictionary**: User-defined text expansions with hot-reload
- 🎯 **Language Rules**: Configurable formality, slang, emoji frequency
- 🛡️ **No-Mean Filter**: Blocks spam and keyboard mashing
- 📱 **Mobile-Ready**: ONNX export for iOS/Android deployment

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Training Pipeline

```bash
./scripts/train_pipeline.sh
```

This will:
- Create sample training data
- Train SentencePiece tokenizer
- Train TinyLSTM model
- Export to ONNX format
- Test prediction engine

### 3. Test Predictions

```python
from src.inference.prediction_engine import PredictionEngine

engine = PredictionEngine(
    model_path="models/best_model.pt",
    tokenizer_path="models/tokenizer.model",
    dictionary_path="config/custom_dictionary.json"
)

# Get suggestions
suggestions = engine.get_suggestions("I'm going to", language="en")
print(suggestions)  # ['the', 'be', 'go', ...]
```

## Project Structure

```
Keyboard-Suggestions-AI/
├── src/
│   ├── model/           # TinyLSTM model
│   ├── tokenizer/       # SentencePiece tokenizer
│   ├── dictionary/      # Custom dictionary system
│   ├── rules/           # Language rules & filters
│   ├── inference/       # Prediction engine
│   └── utils/           # Utilities
├── config/              # Configuration files
├── data/                # Training data
├── models/              # Trained models
├── test-data/           # Test examples
└── scripts/             # Training scripts
```

## Configuration

### Model Config (`config/model_config.yaml`)

```yaml
model:
  embedding_dim: 64
  hidden_dim: 128
  num_layers: 1
  vocab_size: 25000
```

### Language Rules (`config/language_rules.yaml`)

```yaml
languages:
  en:
    formality: "casual"
    emoji_frequency: "high"
    boost_tokens: ["gonna", "wanna", "lol"]
  ja:
    formality: "polite"
    emoji_frequency: "low"
    boost_tokens: ["です", "ます"]
```

## Custom Dictionary

Add custom text expansions:

```python
from src.dictionary.custom_dict import CustomDictionary

dictionary = CustomDictionary("config/custom_dictionary.json")
dictionary.add("ty", "thank you")
dictionary.add("brb", "be right back")
dictionary.save("config/custom_dictionary.json")
```

## Model Performance

| Metric | Target | Achieved |
|--------|--------|----------|
| Model Size | <5 MB | ~1.4 MB |
| Latency | <50 ms | TBD |
| Top-3 Accuracy | >70% | TBD |

## Mobile Integration

### iOS (Core ML)

1. Convert ONNX to Core ML:
```bash
pip install coremltools
python scripts/convert_to_coreml.py
```

2. Add to Xcode project
3. Load in keyboard extension

### Android (TensorFlow Lite)

1. Convert ONNX to TFLite:
```bash
python scripts/convert_to_tflite.py
```

2. Add to Android project
3. Load in keyboard service

## Development Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed development plan.

## Testing

Run tests with example data:

```bash
python -m pytest tests/
```

Test with custom examples:

```bash
python src/inference/prediction_engine.py
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.
