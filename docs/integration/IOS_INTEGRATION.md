# iOS Integration Guide

Complete guide for integrating KeyboardAI into your iOS keyboard extension.

---

## Package Contents

After running `./scripts/build_ios_package.sh`, you'll have:

```
ios/KeyboardAI/
├── KeyboardAI.mlpackage      # Core ML model
├── tokenizer.model            # SentencePiece tokenizer
├── tokenizer.vocab            # Vocabulary file
├── language_rules.yaml        # Language rules
├── custom_dictionary.json     # Custom dictionary
├── model_info.json           # Model metadata
└── README.md                 # Package info
```

---

## Requirements

- **iOS**: 15.0+
- **Xcode**: 13.0+
- **Swift**: 5.5+
- **Dependencies**:
  - Core ML framework (built-in)
  - SentencePiece Swift wrapper (see below)

---

## Step 1: Add Files to Xcode Project

### 1.1 Add Core ML Model

1. Drag `KeyboardAI.mlpackage` into your Xcode project
2. Check "Copy items if needed"
3. Add to keyboard extension target
4. Xcode will auto-generate Swift interface

### 1.2 Add Resource Files

1. Create `Resources` folder in keyboard extension
2. Add these files:
   - `tokenizer.model`
   - `tokenizer.vocab`
   - `language_rules.yaml`
   - `custom_dictionary.json`
3. Ensure they're added to keyboard extension target

---

## Step 2: Install SentencePiece

### Option A: Swift Package Manager (Recommended)

Add to `Package.swift`:

```swift
dependencies: [
    .package(
        url: "https://github.com/google/sentencepiece-swift",
        from: "0.1.0"
    )
]
```

### Option B: Manual Integration

1. Download SentencePiece C++ library
2. Build for iOS (arm64)
3. Create Swift wrapper (see example below)

---

## Step 3: Create Swift Wrapper Classes

### 3.1 Tokenizer Wrapper

```swift
import Foundation
import SentencePiece // If using SPM

class Tokenizer {
    private var processor: SentencePieceProcessor?
    
    init() {
        guard let modelPath = Bundle.main.path(
            forResource: "tokenizer",
            ofType: "model"
        ) else {
            print("Error: tokenizer.model not found")
            return
        }
        
        processor = SentencePieceProcessor(modelPath: modelPath)
    }
    
    func encode(_ text: String) -> [Int32] {
        guard let processor = processor else { return [] }
        return processor.encode(text)
    }
    
    func decode(_ ids: [Int32]) -> String {
        guard let processor = processor else { return "" }
        return processor.decode(ids)
    }
    
    func idToPiece(_ id: Int32) -> String {
        guard let processor = processor else { return "" }
        return processor.idToPiece(id)
    }
    
    func vocabSize() -> Int {
        guard let processor = processor else { return 0 }
        return processor.vocabSize()
    }
}
```

### 3.2 Model Wrapper

```swift
import CoreML

class KeyboardAIModel {
    private var model: KeyboardAI?
    private let tokenizer: Tokenizer
    
    init() {
        // Load Core ML model
        do {
            let config = MLModelConfiguration()
            config.computeUnits = .cpuAndNeuralEngine // Use Neural Engine
            model = try KeyboardAI(configuration: config)
        } catch {
            print("Error loading model: \(error)")
        }
        
        // Initialize tokenizer
        tokenizer = Tokenizer()
    }
    
    func predict(text: String, topK: Int = 5) -> [String] {
        guard let model = model else { return [] }
        
        // Tokenize input
        let tokenIds = tokenizer.encode(text)
        guard !tokenIds.isEmpty else { return [] }
        
        // Prepare input
        let input = try? KeyboardAIInput(
            input_ids: MLMultiArray(tokenIds)
        )
        
        guard let input = input else { return [] }
        
        // Run inference
        guard let output = try? model.prediction(input: input) else {
            return []
        }
        
        // Get logits
        let logits = output.logits
        
        // Get top-K predictions
        let topIndices = getTopK(logits: logits, k: topK)
        
        // Convert to words
        return topIndices.map { tokenizer.idToPiece(Int32($0)) }
    }
    
    private func getTopK(logits: MLMultiArray, k: Int) -> [Int] {
        // Convert MLMultiArray to array
        let count = logits.count
        var scores: [(index: Int, value: Float)] = []
        
        for i in 0..<count {
            let value = logits[i].floatValue
            scores.append((i, value))
        }
        
        // Sort by score
        scores.sort { $0.value > $1.value }
        
        // Return top-K indices
        return Array(scores.prefix(k).map { $0.index })
    }
}

// Helper extension for MLMultiArray
extension MLMultiArray {
    convenience init(_ array: [Int32]) {
        try! self.init(shape: [1, array.count] as [NSNumber], dataType: .int32)
        for (index, value) in array.enumerated() {
            self[index] = NSNumber(value: value)
        }
    }
}
```

### 3.3 Custom Dictionary

```swift
import Foundation

class CustomDictionary {
    private var entries: [String: String] = [:]
    
    init() {
        loadDictionary()
    }
    
    private func loadDictionary() {
        guard let path = Bundle.main.path(
            forResource: "custom_dictionary",
            ofType: "json"
        ) else { return }
        
        guard let data = try? Data(contentsOf: URL(fileURLWithPath: path)),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let entries = json["entries"] as? [String: [String: Any]] else {
            return
        }
        
        for (key, value) in entries {
            if let expansion = value["value"] as? String {
                self.entries[key.lowercased()] = expansion
            }
        }
    }
    
    func lookup(_ prefix: String) -> [String] {
        let lowercased = prefix.lowercased()
        return entries
            .filter { $0.key.hasPrefix(lowercased) }
            .map { $0.value }
    }
    
    func get(_ key: String) -> String? {
        return entries[key.lowercased()]
    }
}
```

### 3.4 Prediction Engine

```swift
class PredictionEngine {
    private let model: KeyboardAIModel
    private let dictionary: CustomDictionary
    
    init() {
        model = KeyboardAIModel()
        dictionary = CustomDictionary()
    }
    
    func getSuggestions(for text: String, count: Int = 5) -> [String] {
        var suggestions: [String] = []
        
        // 1. Check custom dictionary
        let words = text.split(separator: " ")
        if let lastWord = words.last {
            let customMatches = dictionary.lookup(String(lastWord))
            suggestions.append(contentsOf: customMatches)
        }
        
        // 2. Get model predictions
        if suggestions.count < count {
            let modelPredictions = model.predict(
                text: text,
                topK: count - suggestions.count
            )
            
            // Filter duplicates
            for prediction in modelPredictions {
                if !suggestions.contains(prediction) {
                    suggestions.append(prediction)
                }
            }
        }
        
        // Return top N
        return Array(suggestions.prefix(count))
    }
}
```

---

## Step 4: Integrate into Keyboard Extension

### 4.1 Update KeyboardViewController

```swift
import UIKit

class KeyboardViewController: UIInputViewController {
    
    private var predictionEngine: PredictionEngine!
    private var suggestionBar: UIStackView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Initialize prediction engine
        predictionEngine = PredictionEngine()
        
        // Setup UI
        setupSuggestionBar()
    }
    
    private func setupSuggestionBar() {
        suggestionBar = UIStackView()
        suggestionBar.axis = .horizontal
        suggestionBar.distribution = .fillEqually
        suggestionBar.spacing = 8
        
        view.addSubview(suggestionBar)
        
        // Add constraints
        suggestionBar.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            suggestionBar.topAnchor.constraint(equalTo: view.topAnchor),
            suggestionBar.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 8),
            suggestionBar.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -8),
            suggestionBar.heightAnchor.constraint(equalToConstant: 40)
        ])
    }
    
    override func textDidChange(_ textInput: UITextInput?) {
        // Get current text
        guard let proxy = textDocumentProxy as UITextDocumentProxy?,
              let text = proxy.documentContextBeforeInput else {
            return
        }
        
        // Get suggestions
        let suggestions = predictionEngine.getSuggestions(for: text)
        
        // Update UI
        updateSuggestions(suggestions)
    }
    
    private func updateSuggestions(_ suggestions: [String]) {
        // Clear existing buttons
        suggestionBar.arrangedSubviews.forEach { $0.removeFromSuperview() }
        
        // Add new suggestion buttons
        for suggestion in suggestions {
            let button = UIButton(type: .system)
            button.setTitle(suggestion, for: .normal)
            button.addTarget(
                self,
                action: #selector(suggestionTapped(_:)),
                for: .touchUpInside
            )
            suggestionBar.addArrangedSubview(button)
        }
    }
    
    @objc private func suggestionTapped(_ sender: UIButton) {
        guard let suggestion = sender.title(for: .normal) else { return }
        textDocumentProxy.insertText(suggestion)
    }
}
```

---

## Step 5: Optimize Performance

### 5.1 Lazy Loading

```swift
class PredictionEngine {
    private lazy var model: KeyboardAIModel = {
        return KeyboardAIModel()
    }()
    
    // Only load when first used
}
```

### 5.2 Background Prediction

```swift
private let predictionQueue = DispatchQueue(
    label: "com.yourapp.prediction",
    qos: .userInteractive
)

func getSuggestions(for text: String, completion: @escaping ([String]) -> Void) {
    predictionQueue.async {
        let suggestions = self.predict(text)
        DispatchQueue.main.async {
            completion(suggestions)
        }
    }
}
```

### 5.3 Caching

```swift
private var cache: [String: [String]] = [:]

func getSuggestions(for text: String) -> [String] {
    if let cached = cache[text] {
        return cached
    }
    
    let suggestions = predict(text)
    cache[text] = suggestions
    return suggestions
}
```

---

## Step 6: Memory Management

### 6.1 Monitor Memory Usage

```swift
func checkMemoryUsage() {
    var info = mach_task_basic_info()
    var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4
    
    let kerr: kern_return_t = withUnsafeMutablePointer(to: &info) {
        $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
            task_info(mach_task_self_,
                     task_flavor_t(MACH_TASK_BASIC_INFO),
                     $0,
                     &count)
        }
    }
    
    if kerr == KERN_SUCCESS {
        let usedMB = Double(info.resident_size) / 1024.0 / 1024.0
        print("Memory used: \(usedMB) MB")
    }
}
```

### 6.2 Unload When Needed

```swift
func didReceiveMemoryWarning() {
    // Clear cache
    cache.removeAll()
    
    // Unload model if needed
    model = nil
}
```

---

## Step 7: Testing

### 7.1 Unit Tests

```swift
import XCTest

class KeyboardAITests: XCTestCase {
    var engine: PredictionEngine!
    
    override func setUp() {
        engine = PredictionEngine()
    }
    
    func testPrediction() {
        let suggestions = engine.getSuggestions(for: "I'm going to")
        XCTAssertFalse(suggestions.isEmpty)
        XCTAssertLessThanOrEqual(suggestions.count, 5)
    }
    
    func testCustomDictionary() {
        let suggestions = engine.getSuggestions(for: "ty")
        XCTAssertTrue(suggestions.contains("thank you"))
    }
    
    func testPerformance() {
        measure {
            _ = engine.getSuggestions(for: "Hello world")
        }
        // Should be < 50ms
    }
}
```

---

## Performance Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Prediction Latency | < 50ms | Use `measure {}` in tests |
| Memory Usage | < 30MB | Use Instruments Memory Profiler |
| Model Load Time | < 500ms | Measure in `viewDidLoad` |
| App Extension Size | < 10MB | Check in Xcode build settings |

---

## Troubleshooting

### Model Not Loading

**Problem**: Core ML model fails to load

**Solutions**:
1. Check model is added to keyboard extension target
2. Verify iOS deployment target is 15.0+
3. Check model file isn't corrupted

### High Memory Usage

**Problem**: Keyboard uses too much memory

**Solutions**:
1. Use `.cpuOnly` instead of `.cpuAndNeuralEngine`
2. Implement caching with size limits
3. Unload model when not in use

### Slow Predictions

**Problem**: Predictions take > 100ms

**Solutions**:
1. Use Neural Engine (`.cpuAndNeuralEngine`)
2. Reduce sequence length
3. Implement prediction queue
4. Cache recent predictions

---

## Next Steps

1. ✅ Integrate package into your iOS project
2. ✅ Test on simulator
3. ✅ Test on physical device
4. ✅ Measure performance metrics
5. ✅ Provide feedback on:
   - Prediction latency
   - Memory usage
   - Accuracy
   - Any issues encountered

---

## Support

For issues or questions:
1. Check model_info.json for model details
2. Review error logs in Xcode console
3. Test with example inputs from test-data/
4. Report performance metrics for optimization
