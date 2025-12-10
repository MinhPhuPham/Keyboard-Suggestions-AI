# iOS Integration Guide - Core ML

## ⚠️ Requirements

Before you start, make sure you have:

### 1. Required Files (from training)
- ✅ `ios/KeyboardAI/KeyboardAI.mlpackage` (~25 MB) - Core ML model
- ✅ `ios/KeyboardAI/tokenizer.model` (~788 KB) - SentencePiece tokenizer
- ✅ `ios/KeyboardAI/tokenizer.vocab` (~581 KB) - Vocabulary file
- ✅ `ios/KeyboardAI/model_info.json` - Model metadata

**Get these by running**: `./build-package-complete.sh`

### 2. iOS Development Environment
- ✅ macOS with Xcode 14+ installed
- ✅ iOS 15.0+ deployment target
- ✅ Keyboard extension project created

### 3. Required Dependencies
- ✅ **SentencePiece for Swift** - CRITICAL for tokenization
  
  **Swift Package Manager** (recommended):
  ```
  https://github.com/jkrukowski/swift-sentencepiece
  ```
  
  **Installation**:
  1. In Xcode: File → Add Package Dependencies
  2. Enter URL: `https://github.com/jkrukowski/swift-sentencepiece`
  3. Select "Up to Next Major Version" (1.0.0)
  4. Add to your keyboard extension target

---

Complete guide for integrating the KeyboardAI Core ML model into your iOS keyboard extension.

**Why Core ML?**
- ✅ Native iOS framework (no C++ complexity)
- ✅ Optimized for Apple Silicon
- ✅ Smaller model size with FP16 precision (~300 KB)
- ✅ Lower memory usage
- ✅ Simple Swift API (no Objective-C++ bridge needed)
- ✅ Better battery efficiency

---

## Complete End-to-End Workflow

## Quick Checklist

Use this checklist to track your integration progress:

**Before You Start**:
- [ ] Ran `./build-package-complete.sh` to generate model files
- [ ] Have `KeyboardAI.mlpackage`, `tokenizer.model`, `tokenizer.vocab`
- [ ] Have Xcode 14+ installed
- [ ] Have keyboard extension project created

**Step 1: Setup**:
- [ ] Opened project in Xcode
- [ ] File → Add Package Dependencies
- [ ] Added `https://github.com/jkrukowski/swift-sentencepiece`
- [ ] Selected keyboard extension target for the package

**Step 2: Add Files**:
- [ ] Dragged `KeyboardAI.mlpackage` into Xcode
- [ ] Dragged `tokenizer.model` into Xcode
- [ ] Dragged `tokenizer.vocab` into Xcode
- [ ] Dragged `model_info.json` into Xcode
- [ ] Checked "Copy items if needed"
- [ ] Added all files to keyboard extension target

**Step 3: Verify**:
- [ ] Files appear in Build Phases → Copy Bundle Resources
- [ ] Target Membership shows keyboard extension checked
- [ ] Clean build folder (⇧⌘K)
- [ ] Build succeeds (⌘B)

**Step 4: Code**:
- [ ] Created `Tokenizer.swift` with SentencePiece
- [ ] Created `KeyboardAIModel.swift` with fixed prediction
- [ ] Integrated into keyboard view controller
- [ ] Tested on simulator
- [ ] Tested on device

---

### Overview

```
Train Model → Export to Core ML → Add to Xcode → Integrate in Swift
```

### Quick Start (If Model Already Trained)

If you already have `models/best_model.pt`:

```bash
# 1. Create Python 3.11 environment for Core ML export
conda create -n coreml-export python=3.11 -y
conda activate coreml-export

# 2. Install coremltools
pip install coremltools torch sentencepiece pyyaml

# 3. Export to Core ML
python scripts/export_coreml.py \
    --model models/best_model.pt \
    --output ios/KeyboardAI \
    --name KeyboardAI
```

**Output**:
- `ios/KeyboardAI/KeyboardAI.mlpackage` (~300-500 KB)
- `ios/KeyboardAI/model_info.json`

Then skip to **Step 2** below.

### Full Workflow (From Scratch)

If you need to train the model first:

```bash
# 1. Train model (in your main Python 3.13 environment)
./build-package-complete.sh --quick  # Quick 5-epoch training

# 2. Switch to Python 3.11 for Core ML export
conda create -n coreml-export python=3.11 -y
conda activate coreml-export
pip install coremltools torch sentencepiece pyyaml

# 3. Export to Core ML
python scripts/export_coreml.py
```

---

## Prerequisites

- **iOS**: 15.0+ (for Core ML)
- **Xcode**: 13.0+
- **Swift**: 5.0+
- **Python**: 3.9-3.12 (for coremltools export)

---

## Step 1: Export Model to Core ML

### 1.1 Install coremltools

```bash
# Create Python 3.11 environment (coremltools doesn't support 3.13)
conda create -n coreml-export python=3.11
conda activate coreml-export

# Install dependencies
pip install coremltools torch
```

### 1.2 Export Model

```bash
# Export trained model to Core ML
python scripts/export_coreml.py \
    --model models/best_model.pt \
    --output ios/KeyboardAI \
    --name KeyboardAI
```

**Output**:
- `ios/KeyboardAI/KeyboardAI.mlpackage` (~300-500 KB with FP16)
- `ios/KeyboardAI/model_info.json` (metadata)

### 1.3 Important Notes

**Why Python 3.11?**
- `coremltools` requires Python 3.9-3.12
- Your main environment uses Python 3.13 (for training)
- You need a separate environment for Core ML export

**What if export fails?**

Common issues:
1. **coremltools not installed**: Run `pip install coremltools`
2. **Wrong Python version**: Use Python 3.9-3.12, not 3.13
3. **Model not found**: Train model first with `./build-package-complete.sh`
4. **LSTM compatibility**: The export script uses `torch.jit.trace` which works with LSTMs

**Verify export worked**:
```bash
# Check output exists
ls -lh ios/KeyboardAI/KeyboardAI.mlpackage
ls -lh ios/KeyboardAI/model_info.json

# Should see:
# KeyboardAI.mlpackage/ (directory, ~300-500 KB)
# model_info.json (metadata file)
```

---

## Step 2: Setup Xcode Project

### 2.1 Create Keyboard Extension

1. Open your iOS app project in Xcode
2. **File → New → Target**
3. Select **Custom Keyboard Extension**
4. Name it (e.g., "SmartKeyboard")
5. Click **Finish**

### 2.2 Add Core ML Model

1. Drag `KeyboardAI.mlpackage` into your keyboard extension target
2. **Important**: Check "Copy items if needed" and add to keyboard extension target
3. Xcode will automatically generate Swift classes for the model

**Verify**:
- File Inspector → Target Membership → Your keyboard extension is checked ✅
- Build Phases → Copy Bundle Resources → `KeyboardAI.mlpackage` is listed

### 2.3 Add Other Required Files

Also add these files to your keyboard extension (from `ios/KeyboardAI/`):

**Required**:
- ✅ `tokenizer.model` - SentencePiece tokenizer (needed for encoding text)
- ✅ `tokenizer.vocab` - Vocabulary file (needed for decoding)
- ✅ `model_info.json` - Model metadata (contains vocab size)

**Optional** (for advanced features):
- `language_rules.yaml` - Language-specific rules
- `custom_dictionary.json` - Custom dictionary

**How to add**:
1. Drag all files from `ios/KeyboardAI/` into Xcode
2. Check "Copy items if needed"
3. Add to keyboard extension target
4. Verify in Build Phases → Copy Bundle Resources

**Your keyboard extension should have**:
```
Resources/
├── KeyboardAI.mlpackage     ← Core ML model
├── tokenizer.model          ← Required for tokenization
├── tokenizer.vocab          ← Required for decoding
└── model_info.json          ← Required for vocab size
```

---

## Step 3: Create Model Wrapper (Pure Swift!)

### 3.1 Create KeyboardAIModel.swift

```swift
import Foundation
import CoreML

class KeyboardAIModel {
    private let model: KeyboardAI
    private let tokenizer: Tokenizer
    private let vocabSize: Int
    
    init?() {
        // Load Core ML model
        // Note: Xcode compiles .mlpackage to .mlmodelc
        // Use compiledModelURL or load directly by class name
        do {
            // Option 1: Load by configuration (recommended)
            let config = MLModelConfiguration()
            self.model = try KeyboardAI(configuration: config)
            
            // Option 2: If Option 1 fails, try loading from bundle
            // guard let modelURL = Bundle.main.url(forResource: "KeyboardAI", withExtension: "mlmodelc"),
            //       let model = try? KeyboardAI(contentsOf: modelURL) else {
            //     print("Failed to load Core ML model")
            //     return nil
            // }
            // self.model = model
        } catch {
            print("Failed to load Core ML model: \(error)")
            return nil
        }
        
        // Load tokenizer
        guard let tokenizer = Tokenizer() else {
            print("Failed to load tokenizer")
            return nil
        }
        self.tokenizer = tokenizer
        
        // Read vocab size from metadata
        if let infoPath = Bundle.main.path(forResource: "model_info", ofType: "json"),
           let data = try? Data(contentsOf: URL(fileURLWithPath: infoPath)),
           let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let vocab = json["vocab_size"] as? Int {
            self.vocabSize = vocab
        } else {
            self.vocabSize = 100 // Default
        }
    }
    
    func predict(text: String, topK: Int = 5) -> [String] {
        // Tokenize input text
        let tokenIds = tokenizer.encode(text)
        guard !tokenIds.isEmpty else { return [] }
        
        // Take last 50 tokens (model's max sequence length)
        let input = Array(tokenIds.suffix(50))
        
        // Pad to fixed length if needed
        var paddedInput = input
        while paddedInput.count < 50 {
            paddedInput.insert(0, at: 0) // Pad with 0
        }
        
        // Convert to MLMultiArray
        guard let inputArray = try? MLMultiArray(shape: [1, 50], dataType: .int32) else {
            return []
        }
        
        for (i, tokenId) in paddedInput.enumerated() {
            inputArray[i] = NSNumber(value: tokenId)
        }
        
        // Run inference
        guard let output = try? model.prediction(input_ids: inputArray) else {
            return []
        }
        
        // Get logits for the last token position
        let logits = output.logits
        
        // Extract last token's predictions (shape: [1, 50, vocab_size])
        // We want predictions at position [0, 49, :]
        let lastTokenStart = 49 * vocabSize
        var scores: [(index: Int, score: Float)] = []
        
        for i in 0..<min(vocabSize, 1000) {  // Limit to top 1000 for performance
            let score = logits[lastTokenStart + i].floatValue
            scores.append((index: i, score: score))
        }
        
        // Get top-K token IDs
        let topTokenIds = scores.sorted { $0.score > $1.score }
            .prefix(topK * 3)  // Get more candidates
            .map { $0.index }
        
        // CRITICAL FIX: Decode each predicted token by appending to input
        var suggestions: [String] = []
        let originalText = text
        
        for nextTokenId in topTokenIds {
            // Create sequence: input + predicted token
            let fullSequence = tokenIds + [nextTokenId]
            
            // Decode the full sequence
            let decodedText = tokenizer.decode(fullSequence)
            
            // Extract only the NEW part (what was added)
            if decodedText.hasPrefix(originalText) {
                let newPart = String(decodedText.dropFirst(originalText.count)).trimmingCharacters(in: .whitespaces)
                if !newPart.isEmpty && !suggestions.contains(newPart) {
                    suggestions.append(newPart)
                    if suggestions.count >= topK {
                        break
                    }
                }
            }
        }
        
        return suggestions
    }
}
}
```

### 3.2 Create Tokenizer.swift

**IMPORTANT**: You need to add SentencePiece library to iOS.

**Swift Package Manager** (recommended):
1. In Xcode: **File → Add Package Dependencies**
2. Enter URL: `https://github.com/jkrukowski/swift-sentencepiece`
3. Select "Up to Next Major Version" (1.0.0)
4. Add to keyboard extension target

**Tokenizer.swift**:
```swift
import Foundation
import Sentencepiece  // From swift-sentencepiece package

class Tokenizer {
    private let tokenizer: SentencepieceTokenizer
    let vocabSize: Int
    
    init?() {
        // Load SentencePiece model
        guard let modelPath = Bundle.main.path(forResource: "tokenizer", ofType: "model") else {
            print("Tokenizer model not found")
            return nil
        }
        
        do {
            // Initialize with tokenOffset=0 (not Hugging Face compatible)
            self.tokenizer = try SentencepieceTokenizer(modelPath: modelPath, tokenOffset: 0)
            // Note: No direct vocabularySize property, estimate from model
            self.vocabSize = 32000  // From model_info.json
        } catch {
            print("Failed to load SentencePiece tokenizer: \(error)")
            return nil
        }
    }
    
    func encode(_ text: String) -> [Int] {
        // Encode text to token IDs
        do {
            return try tokenizer.encode(text)
        } catch {
            print("Encoding error: \(error)")
            return []
        }
    }
    
    func decode(_ ids: [Int]) -> String {
        // Decode token IDs back to text
        do {
            return try tokenizer.decode(ids)
        } catch {
            print("Decoding error: \(error)")
            return ""
        }
    }
    
    func encodePieces(_ text: String) -> [String] {
        // Encode to pieces (for debugging)
        do {
            let ids = try tokenizer.encode(text)
            return ids.compactMap { id in
                try? tokenizer.idToToken(id)
            }
        } catch {
            print("Encode pieces error: \(error)")
            return []
        }
    }
}
```

**API Reference** (from swift-sentencepiece):
```swift
// Initialize
let tokenizer = try SentencepieceTokenizer(
    modelPath: path,
    tokenOffset: 0  // 0 for standard, 1 for Hugging Face compatibility
)

// Encode (throws)
let ids = try tokenizer.encode("ありがとう")  // Returns [Int]

// Decode (throws)
let text = try tokenizer.decode(ids)  // Returns String

// Token conversion
let token = try tokenizer.idToToken(id)  // Int -> String
let id = tokenizer.tokenToId(token)      // String -> Int

// Special tokens
let unkId = tokenizer.unkTokenId  // Unknown token ID
let bosId = tokenizer.bosTokenId  // Beginning of sequence
let eosId = tokenizer.eosTokenId  // End of sequence
let padId = tokenizer.padTokenId  // Padding token

// Normalization
let normalized = try tokenizer.normalize(text)
```

**Why This Fixes the Issue**:

**Before** (hash-based):
```swift
// ❌ Wrong: Returns random hash values
func encode(_ text: String) -> [Int] {
    let words = text.components(separatedBy: .whitespaces)
    return words.map { abs($0.hashValue % vocabSize) }  // Random!
}
```

**After** (SentencePiece):
```swift
// ✅ Correct: Uses trained tokenizer
func encode(_ text: String) -> [Int] {
    return processor.encode(text).map { Int($0) }  // Proper tokenization
}
```

---

## Step 4: Integrate into Keyboard

### 4.1 Update KeyboardViewController.swift

```swift
import UIKit

class KeyboardViewController: UIInputViewController {
    
    private var model: KeyboardAIModel?
    private var suggestionBar: UIStackView!
    private var predictionCache: [String: [String]] = [:]
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Load model (lazy loading for better performance)
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            self?.model = KeyboardAIModel()
            if self?.model == nil {
                print("Failed to initialize model")
            }
        }
        
        // Setup UI
        setupSuggestionBar()
    }
    
    private func setupSuggestionBar() {
        suggestionBar = UIStackView()
        suggestionBar.axis = .horizontal
        suggestionBar.distribution = .fillEqually
        suggestionBar.spacing = 4
        suggestionBar.backgroundColor = .systemGray6
        
        view.addSubview(suggestionBar)
        
        suggestionBar.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            suggestionBar.topAnchor.constraint(equalTo: view.topAnchor),
            suggestionBar.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            suggestionBar.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            suggestionBar.heightAnchor.constraint(equalToConstant: 40)
        ])
    }
    
    override func textDidChange(_ textInput: UITextInput?) {
        guard let proxy = textDocumentProxy as UITextDocumentProxy?,
              let text = proxy.documentContextBeforeInput,
              !text.isEmpty else {
            clearSuggestions()
            return
        }
        
        updateSuggestions(for: text)
    }
    
    private func updateSuggestions(for text: String) {
        // Check cache first
        if let cached = predictionCache[text] {
            displaySuggestions(cached)
            return
        }
        
        guard let model = model else { return }
        
        // Get predictions in background
        DispatchQueue.global(qos: .userInteractive).async { [weak self] in
            let suggestions = model.predict(text: text, topK: 3)
            
            // Cache result
            self?.predictionCache[text] = suggestions
            
            // Limit cache size
            if self?.predictionCache.count ?? 0 > 100 {
                self?.predictionCache.removeAll()
            }
            
            DispatchQueue.main.async {
                self?.displaySuggestions(suggestions)
            }
        }
    }
    
    private func displaySuggestions(_ suggestions: [String]) {
        // Clear existing
        suggestionBar.arrangedSubviews.forEach { $0.removeFromSuperview() }
        
        // Add new suggestions
        for suggestion in suggestions {
            let button = UIButton(type: .system)
            button.setTitle(suggestion, for: .normal)
            button.titleLabel?.font = .systemFont(ofSize: 16)
            button.addTarget(self, action: #selector(suggestionTapped(_:)), for: .touchUpInside)
            suggestionBar.addArrangedSubview(button)
        }
    }
    
    private func clearSuggestions() {
        suggestionBar.arrangedSubviews.forEach { $0.removeFromSuperview() }
    }
    
    @objc private func suggestionTapped(_ sender: UIButton) {
        guard let suggestion = sender.title(for: .normal) else { return }
        textDocumentProxy.insertText(suggestion + " ")
    }
}
```

---

## Step 5: Test

### 5.1 Build and Run

1. Select your keyboard extension scheme
2. Build (⌘B)
3. Run on simulator or device
4. **Settings → General → Keyboard → Keyboards → Add New Keyboard**
5. Select your keyboard
6. Test in any app (Messages, Notes, etc.)

### 5.2 Debug

View logs in Xcode console while keyboard is active.

---

## Performance Optimization

### 1. Lazy Loading

```swift
private lazy var model: KeyboardAIModel? = {
    return KeyboardAIModel()
}()
```

### 2. Prediction Caching

```swift
private var cache: [String: [String]] = [:]

func getCachedPredictions(for text: String) -> [String]? {
    return cache[text]
}
```

### 3. Debouncing

```swift
private var predictionTimer: Timer?

func debouncedPredict(text: String) {
    predictionTimer?.invalidate()
    predictionTimer = Timer.scheduledTimer(withTimeInterval: 0.3, repeats: false) { _ in
        self.updateSuggestions(for: text)
    }
}
```

### 4. Background Loading

```swift
override func viewDidLoad() {
    super.viewDidLoad()
    
    // Load model in background
    DispatchQueue.global(qos: .userInitiated).async {
        self.model = KeyboardAIModel()
    }
}
```

---

## Troubleshooting

### Model Not Loading

**Error**: "Failed to load Core ML model"

**Solutions**:

**1. Check file is in target**:
- Select `KeyboardAI.mlpackage` in Xcode
- File Inspector → Target Membership
- Ensure your keyboard extension is checked ✅

**2. Verify bundle resources**:
- Select your keyboard extension target
- Build Phases → Copy Bundle Resources
- `KeyboardAI.mlpackage` should be listed

**3. Use correct loading method**:
```swift
// ✅ Recommended: Load by configuration
let config = MLModelConfiguration()
let model = try KeyboardAI(configuration: config)

// ✅ Alternative: Load from compiled model
// Xcode compiles .mlpackage to .mlmodelc
guard let modelURL = Bundle.main.url(forResource: "KeyboardAI", withExtension: "mlmodelc") else {
    print("Model not found in bundle")
    return nil
}
let model = try KeyboardAI(contentsOf: modelURL)
```

**4. Check model was added correctly**:
- Clean build folder (⇧⌘K)
- Rebuild (⌘B)
- Check build output for "Compiling KeyboardAI.mlpackage"

**5. Verify in simulator/device**:
```swift
// Debug: Print bundle contents
if let bundlePath = Bundle.main.resourcePath {
    print("Bundle path: \(bundlePath)")
    let files = try? FileManager.default.contentsOfDirectory(atPath: bundlePath)
    print("Bundle files: \(files ?? [])")
}
```

---

### Tokenizer Not Loading

**Error**: "Failed to load tokenizer"

**Cause**: Missing `tokenizer.model` or `tokenizer.vocab` files

**Solution**:

**1. Verify files are in bundle**:
- Check `tokenizer.model` is in Copy Bundle Resources
- Check `tokenizer.vocab` is in Copy Bundle Resources
- Check `model_info.json` is in Copy Bundle Resources

**2. Debug: Print what's in bundle**:
```swift
if let bundlePath = Bundle.main.resourcePath {
    let files = try? FileManager.default.contentsOfDirectory(atPath: bundlePath)
    print("Bundle files: \(files ?? [])")
    
    // Check specific files
    if let tokenizerPath = Bundle.main.path(forResource: "tokenizer", ofType: "model") {
        print("✅ tokenizer.model found at: \(tokenizerPath)")
    } else {
        print("❌ tokenizer.model NOT FOUND")
    }
}
```

**3. Add missing files**:
- Drag `tokenizer.model`, `tokenizer.vocab`, `model_info.json` from `ios/KeyboardAI/`
- Check "Copy items if needed"
- Add to keyboard extension target
- Clean and rebuild

---

### SentencePiece Package Issues

**Error**: Cannot find package or import fails

**Solution - Use Swift Package Manager**:

**1. Add Package in Xcode**:
```
File → Add Package Dependencies
URL: https://github.com/jkrukowski/swift-sentencepiece
Version: Up to Next Major (1.0.0)
```

**2. Import in Swift**:
```swift
import Sentencepiece  // Correct import name
```

**3. Verify installation**:
- Check Package Dependencies in Project Navigator
- Should see "swift-sentencepiece" listed
- Build (⌘B) should succeed

**4. If package fails to resolve**:
```bash
# Clear package cache
rm -rf ~/Library/Caches/org.swift.swiftpm
rm -rf ~/Library/Developer/Xcode/DerivedData

# In Xcode: File → Packages → Reset Package Caches
```

**5. Alternative: Manual installation**:

If Swift Package Manager doesn't work, you can build SentencePiece manually:

```bash
# Clone the repository
git clone https://github.com/jkrukowski/swift-sentencepiece
cd swift-sentencepiece

# Build with Swift
swift build -c release

# Copy built framework to your project
# Then add as a local framework in Xcode
```

---

### Memory Issues

**Error**: Keyboard crashes or is killed

**Solution**:
- iOS limits keyboard extensions to ~30MB memory
- Core ML model (~500KB) + tokenizer (~250KB) should be fine
- Implement caching carefully
- Release resources when not in use
- Clear prediction cache periodically

### Slow Predictions

**Issue**: Predictions take too long

**Solution**:
- Use prediction caching
- Implement debouncing (300ms delay)
- Run predictions in background queue
- Consider reducing model size further

---

## Model Size Comparison

| Format | Size | iOS Support | Complexity |
|--------|------|-------------|------------|
| PyTorch Mobile | ~500 KB | ⚠️ C++17 required | High (Objective-C++) |
| **Core ML** | **~300 KB** | **✅ Native** | **Low (Pure Swift)** |

**Core ML Advantages**:
- 40% smaller with FP16 precision
- No C++ dependencies
- Native iOS optimization
- Better battery life
- Simpler integration

---

## Next Steps

1. ✅ Test on physical device
2. ✅ Measure prediction latency (should be <50ms)
3. ✅ Monitor memory usage
4. ✅ Collect real training data and retrain
5. ✅ Submit to App Store

---

## Resources

- [Core ML Documentation](https://developer.apple.com/documentation/coreml)
- [coremltools Documentation](https://coremltools.readme.io/)
- [iOS Keyboard Extension Guide](https://developer.apple.com/documentation/uikit/keyboards_and_input/creating_a_custom_keyboard)
