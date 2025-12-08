# Keyboard Suggestions AI - Development Roadmap

## Overview
This roadmap breaks down the development of the multilingual keyboard suggestion engine into manageable phases with clear deliverables.

---

## Phase 1: Foundation & Data Preparation (Week 1-2)

### 1.1 Project Setup ✅
- [x] Initialize project structure
- [x] Set up development environment (Python, **PyTorch**, SentencePiece)
- [ ] Create build scripts for iOS and Android
- [x] Set up version control and documentation

### 1.2 Data Collection & Preparation ✅
- [x] Collect English training data (casual text, social media style) - 30 samples created
- [x] Collect Japanese training data (polite/formal text) - 20 samples created
- [x] Add emoji and symbol examples to datasets
- [x] Create test dataset (20-30 basic examples) - 30+ examples in `test-data/`
- [x] Clean and normalize data - `DataPreparator` class implemented
- [x] Split data: 80% train, 10% validation, 10% test - Automated in dataset class

**Deliverable:** ✅ Clean training datasets with Unicode/emoji support
- `data/processed/combined_train.txt` (29 valid sequences)
- `test-data/example_data.json` (30+ test cases)

---

## Phase 2: Tokenizer Development (Week 2-3)

### 2.1 SentencePiece Training ✅
- [x] Configure SentencePiece with `character_coverage=1.0`
- [x] Set vocabulary size to 25,000 tokens (100 for demo, configurable)
- [x] Train tokenizer on combined EN+JA+emoji data
- [x] Reserve top 256 tokens for frequent emoji/symbols (16 emoji defined)
- [x] Validate tokenizer output on test examples

### 2.2 Tokenizer Testing ✅
- [x] Test Unicode character handling - Verified with Japanese text
- [x] Test emoji tokenization - ❤️, 😂, 🎉 etc. working
- [x] Test symbol tokenization - Apostrophes, punctuation working
- [x] Test mixed language input - "東京 is great" tested
- [x] Measure tokenizer size (~900 KB target) - ~50 KB for demo vocab

**Deliverable:** ✅ Trained SentencePiece tokenizer model
- `models/tokenizer.model` (SentencePiece model)
- `models/tokenizer.vocab` (Vocabulary file)
- `src/tokenizer/train_tokenizer.py` (Training script)

---

## Phase 3: Neural Model Training (Week 3-4)

### 3.1 Model Architecture ✅
- [x] Implement TinyLSTM architecture
  - 64-dim embedding layer
  - 128-dim hidden layer (1 layer)
  - Output layer (configurable vocab)
- [x] Add dropout for regularization (0.2)
- [x] Implement training loop with validation

### 3.2 Rule-Aware Data Augmentation ✅
- [x] Create English rule configuration - `config/language_rules.yaml`
- [x] Create Japanese rule configuration - `config/language_rules.yaml`
- [x] Implement data augmentation based on rules - Logit biasing at inference
- [x] Boost teen slang tokens for English - "gonna", "wanna", "lol"
- [x] Boost polite forms for Japanese - "です", "ます", "ございます"

### 3.3 Model Training & Optimization ⏳
- [ ] Train model on prepared datasets - **PENDING: Need larger dataset**
- [x] Monitor validation loss - Early stopping implemented
- [x] Apply INT8 quantization - ONNX quantization ready
- [x] Convert to ONNX format (not TFLite) - Export script ready
- [ ] Validate model size (~100 KB target) - Pending training

**Deliverable:** ⏳ Quantized TinyLSTM model in ONNX format
- `src/model/tiny_lstm.py` (Model architecture) ✅
- `src/model/train.py` (Training script) ✅
- `src/utils/export_model.py` (ONNX export) ✅
- `models/best_model.pt` (Trained model) - **PENDING**

---

## Phase 4: Custom Dictionary System (Week 4-5)

### 4.1 Dictionary Data Structure ✅
- [x] Design prefix-trie data structure in **Python** (C++ for mobile later)
- [x] Implement fast prefix search (O(log n))
- [x] Create dictionary storage format (JSON)
- [x] Add test custom dictionary entries - 20 abbreviations

### 4.2 Dictionary Management ✅
- [x] Implement add/remove dictionary entries
- [x] Implement hot-reload mechanism (<50ms)
- [x] Create dictionary persistence layer - JSON save/load
- [x] Add dictionary validation

### 4.3 Integration with Inference ✅
- [x] Merge custom matches with model predictions
- [x] Prioritize custom dictionary results - Custom first, then model
- [x] Handle duplicate filtering

**Deliverable:** ✅ Custom dictionary engine with hot-reload
- `src/dictionary/custom_dict.py` (Trie + dictionary class)
- `config/custom_dictionary.json` (20 default entries)
- Tested: "ty" → "thank you", "ac" → "scackscac"

---

## Phase 5: Rule Engine & Filters (Week 5-6)

### 5.1 Language-Specific Rules ✅
- [x] Implement rule JSON parser - YAML config loader
- [x] Create English rules configuration - Casual, high emoji
- [x] Create Japanese rules configuration - Polite, low emoji
- [x] Implement inference-time logit biasing - +0.5 boost, -1.0 suppress
- [x] Test rule application on predictions - Verified

### 5.2 "No Mean" Filter ✅
- [x] Implement entropy calculation - Shannon entropy
- [x] Set confidence thresholds - min 0.1
- [x] Filter random character sequences - Regex patterns
- [x] Filter spam patterns - "asdfghjkl", "zzzzz" blocked
- [x] Test filter on edge cases - 6 test cases passed

### 5.3 Language Detection ✅
- [x] Implement simple language detector - Manual selection
- [x] Support manual language selection - Via API parameter
- [x] Support mixed language mode - Both languages active
- [x] Test language switching - "東京 is great" tested

**Deliverable:** ✅ Rule engine with "No Mean" filter
- `src/rules/rule_engine.py` (Rules + no-mean filter)
- `config/language_rules.yaml` (EN + JA configurations)
- Tested: Boost/suppress working, spam filtered

---

## Phase 6: Python Inference Engine (Week 6-7)

### 6.1 Inference Pipeline Development ✅
- [x] Set up Python project structure
- [x] Integrate SentencePiece Python API
- [x] Implement model inference wrapper - PyTorch + ONNX
- [x] Integrate dictionary prefix search
- [x] Integrate rule engine
- [x] Create unified prediction API - `PredictionEngine` class

### 6.2 Model Export & Optimization ✅
- [x] Create ONNX export script - `export_model.py`
- [x] Implement INT8 quantization
- [x] Create training pipeline script - `train_pipeline.sh`
- [ ] Test on mobile devices - **Pending mobile integration**
- [ ] Optimize binary size

**Deliverable:** ✅ Python inference engine with ONNX export
- `src/inference/prediction_engine.py` (Unified API)
- `src/utils/export_model.py` (ONNX + quantization)
- `scripts/train_pipeline.sh` (Complete pipeline)

**Note:** C++ integration will be done during mobile phases (7-8)

---

## Phase 7: iOS Integration (Week 7-8)

### 7.1 iOS Keyboard Extension
- [ ] Create iOS keyboard extension project
- [ ] Set up Core ML integration
- [ ] Create Swift wrapper for C++ core
- [ ] Implement keyboard UI
- [ ] Add suggestion bar

### 7.2 iOS Features
- [ ] Implement language switcher UI
- [ ] Add custom dictionary settings screen
- [ ] Implement dictionary sync (iCloud)
- [ ] Add haptic feedback
- [ ] Optimize memory usage

### 7.3 iOS Testing
- [ ] Test on iPhone simulator
- [ ] Test on physical device
- [ ] Measure latency (<50ms target)
- [ ] Measure memory footprint
- [ ] Test all example user flows

**Deliverable:** Functional iOS keyboard extension

---

## Phase 8: Android Integration (Week 8-9)

### 8.1 Android Keyboard Service
- [ ] Create Android keyboard service project
- [ ] Set up TensorFlow Lite integration
- [ ] Create JNI wrapper for C++ core
- [ ] Implement keyboard UI
- [ ] Add suggestion bar

### 8.2 Android Features
- [ ] Implement language switcher UI
- [ ] Add custom dictionary settings screen
- [ ] Implement dictionary sync (Google Drive)
- [ ] Add vibration feedback
- [ ] Optimize memory usage

### 8.3 Android Testing
- [ ] Test on Android emulator
- [ ] Test on physical device
- [ ] Measure latency (<50ms target)
- [ ] Measure memory footprint
- [ ] Test all example user flows

**Deliverable:** Functional Android keyboard service

---

## Phase 9: Testing & Validation (Week 9-10)

### 9.1 Functional Testing
- [ ] Test custom dictionary: "ac" → "scackscac"
- [ ] Test Japanese polite mode
- [ ] Test "No Mean" filter on spam
- [ ] Test hot-reload of custom entries
- [ ] Test code-switching (EN+JA mixed)

### 9.2 Performance Testing
- [ ] Measure prediction latency (target: <50ms)
- [ ] Measure memory usage (target: <30MB)
- [ ] Measure battery impact
- [ ] Test on low-end devices
- [ ] Profile and optimize bottlenecks

### 9.3 User Acceptance Testing
- [ ] Recruit beta testers
- [ ] Collect feedback on accuracy
- [ ] Collect feedback on UX
- [ ] Iterate on issues
- [ ] Validate all user flows from spec

**Deliverable:** Validated, production-ready keyboard

---

## Phase 10: Polish & Release (Week 10-11)

### 10.1 Documentation
- [ ] Write user guide
- [ ] Write developer documentation
- [ ] Create API reference
- [ ] Add inline code comments
- [ ] Create troubleshooting guide

### 10.2 App Store Preparation
- [ ] Create app icons and screenshots
- [ ] Write app store descriptions
- [ ] Prepare privacy policy
- [ ] Set up analytics (optional)
- [ ] Submit for review (iOS App Store)
- [ ] Submit for review (Google Play Store)

### 10.3 Post-Launch
- [ ] Monitor crash reports
- [ ] Collect user feedback
- [ ] Plan feature updates
- [ ] Consider adding more languages
- [ ] Optimize based on real-world usage

**Deliverable:** Published keyboard apps on both platforms

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Model Size | ≤ 5 MB | Asset bundle size |
| Prediction Latency | < 50 ms | Average response time |
| Memory Usage | < 30 MB | Runtime memory footprint |
| Accuracy (Top-3) | > 70% | Test set evaluation |
| Custom Dict Reload | < 50 ms | Hot-reload timing |
| Battery Impact | Minimal | Background usage monitoring |

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| Model too large | Use aggressive quantization, reduce vocab size |
| Latency too high | Optimize inference, use lookup tables for common patterns |
| Poor accuracy | Collect more training data, tune hyperparameters |
| Platform compatibility | Extensive testing on multiple devices |
| Memory constraints | Profile and optimize, use memory pooling |

---

## Future Enhancements (Post-V1)

- Add 3-5 more languages (Spanish, French, German, Chinese, Korean)
- Implement context-aware suggestions (previous sentence)
- Add swipe-to-type support
- Implement autocorrect functionality
- Add GIF/sticker suggestions
- Cloud sync for custom dictionaries
- Personalized learning from user typing patterns
