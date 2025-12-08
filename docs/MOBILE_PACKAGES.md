# Mobile Deployment Package Structure

This document explains the structure and contents of the iOS and Android deployment packages.

---

## Directory Structure

```
Keyboard-Suggestions-AI/
├── ios/
│   └── KeyboardAI/
│       ├── KeyboardAI.mlpackage      # Core ML model
│       ├── tokenizer.model            # SentencePiece tokenizer
│       ├── tokenizer.vocab            # Vocabulary
│       ├── language_rules.yaml        # Language rules
│       ├── custom_dictionary.json     # Custom dictionary
│       ├── model_info.json           # Metadata
│       └── README.md                 # Package info
│
├── android/
│   └── KeyboardAI/
│       ├── keyboard_ai_int8.tflite   # TFLite model (quantized)
│       ├── tokenizer.model            # SentencePiece tokenizer
│       ├── tokenizer.vocab            # Vocabulary
│       ├── language_rules.yaml        # Language rules
│       ├── custom_dictionary.json     # Custom dictionary
│       ├── model_info.json           # Metadata
│       └── README.md                 # Package info
│
└── docs/
    └── integration/
        ├── IOS_INTEGRATION.md         # iOS integration guide
        └── ANDROID_INTEGRATION.md     # Android integration guide
```

---

## Package Contents

### Core Files (Both Platforms)

#### 1. Model Files

**iOS**: `KeyboardAI.mlpackage`
- Format: Core ML package
- Precision: FLOAT16
- Size: ~100-200 KB (after quantization)
- Input: Token IDs (Int array)
- Output: Logits (Float array)

**Android**: `keyboard_ai_int8.tflite`
- Format: TensorFlow Lite
- Precision: INT8 quantized
- Size: ~50-100 KB (after quantization)
- Input: Token IDs (Int32 array)
- Output: Logits (Float array)

#### 2. Tokenizer Files

**tokenizer.model**
- SentencePiece model file
- Size: ~50 KB (demo) to ~900 KB (production)
- Supports: Unicode, emoji, multilingual

**tokenizer.vocab**
- Vocabulary file
- Contains token-to-ID mappings
- Size: ~10-50 KB

#### 3. Configuration Files

**language_rules.yaml**
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

**custom_dictionary.json**
```json
{
  "version": "1.0",
  "entries": {
    "ty": {"value": "thank you", "priority": 1},
    "brb": {"value": "be right back", "priority": 1}
  }
}
```

#### 4. Metadata

**model_info.json**
```json
{
  "model_name": "KeyboardAI",
  "version": "1.0.0",
  "vocab_size": 25000,
  "embedding_dim": 64,
  "hidden_dim": 128,
  "model_size_mb": 0.15,
  "min_ios_version": "15.0",
  "min_android_api": 21
}
```

---

## Building Packages

### Quick Build

```bash
# Build both iOS and Android packages
./scripts/build_mobile_packages.sh
```

### Individual Platforms

```bash
# iOS only
./scripts/build_ios_package.sh

# Android only
./scripts/build_android_package.sh
```

### Prerequisites

1. **Trained Model**: `models/best_model.pt`
   ```bash
   python src/model/train.py
   ```

2. **Trained Tokenizer**: `models/tokenizer.model`
   ```bash
   python src/tokenizer/train_tokenizer.py
   ```

3. **Dependencies**:
   ```bash
   pip install coremltools onnx-tf tensorflow
   ```

---

## Package Sizes

### Expected Sizes (Production)

| Component | iOS | Android |
|-----------|-----|---------|
| Model | ~150 KB | ~80 KB |
| Tokenizer | ~900 KB | ~900 KB |
| Config | ~10 KB | ~10 KB |
| **Total** | **~1.1 MB** | **~1.0 MB** |

### Demo Sizes (Current)

| Component | iOS | Android |
|-----------|-----|---------|
| Model | ~100 KB | ~50 KB |
| Tokenizer | ~50 KB | ~50 KB |
| Config | ~10 KB | ~10 KB |
| **Total** | **~160 KB** | **~110 KB** |

---

## Integration Overview

### iOS Integration Steps

1. Add `KeyboardAI.mlpackage` to Xcode project
2. Copy resource files to app bundle
3. Implement Swift wrapper classes
4. Integrate into keyboard extension
5. Test and optimize

**See**: [IOS_INTEGRATION.md](integration/IOS_INTEGRATION.md)

### Android Integration Steps

1. Add TFLite model to assets folder
2. Copy resource files to assets
3. Implement Kotlin/Java wrapper classes
4. Integrate into keyboard service
5. Test and optimize

**See**: [ANDROID_INTEGRATION.md](integration/ANDROID_INTEGRATION.md)

---

## Performance Targets

| Metric | Target | iOS | Android |
|--------|--------|-----|---------|
| Prediction Latency | < 50ms | Measure with Instruments | Measure with Profiler |
| Memory Usage | < 30MB | Check in Xcode | Check with ActivityManager |
| Model Load Time | < 500ms | Measure in viewDidLoad | Measure in onCreate |
| Package Size | < 5MB | Check IPA size | Check APK size |

---

## Testing Checklist

### Before Deployment

- [ ] Model trained and exported
- [ ] Tokenizer trained
- [ ] Configuration files updated
- [ ] Packages built successfully
- [ ] Integration guides reviewed

### After Integration

- [ ] Model loads correctly
- [ ] Predictions work
- [ ] Custom dictionary works
- [ ] Language rules apply
- [ ] Performance meets targets
- [ ] Memory usage acceptable
- [ ] No crashes or errors

---

## Troubleshooting

### Build Fails

**Problem**: Package build script fails

**Solutions**:
1. Check model exists: `models/best_model.pt`
2. Check tokenizer exists: `models/tokenizer.model`
3. Install dependencies: `pip install -r requirements.txt`
4. Check Python version: 3.8+

### Large Package Size

**Problem**: Package is > 5MB

**Solutions**:
1. Use INT8 quantization
2. Reduce vocabulary size
3. Use FLOAT16 precision (iOS)
4. Remove unused config files

### Model Not Loading

**Problem**: Model fails to load on device

**Solutions**:
1. Check file paths
2. Verify model format
3. Check iOS/Android version compatibility
4. Review integration guide

---

## Updating Packages

### When to Rebuild

- After retraining model
- After updating tokenizer
- After changing language rules
- After modifying custom dictionary
- For performance optimization

### How to Update

1. Train new model/tokenizer
2. Run build script
3. Replace old package files
4. Test in mobile app
5. Measure performance changes

---

## Support

For integration help:
1. Review integration guides
2. Check model_info.json for details
3. Test with example inputs
4. Report issues with:
   - Platform (iOS/Android)
   - Error messages
   - Performance metrics
   - Device info
