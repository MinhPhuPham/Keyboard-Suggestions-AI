# iOS Integration Guide - PyTorch Mobile

Complete step-by-step guide for integrating the KeyboardAI TorchScript model into your iOS keyboard extension.

---

## Prerequisites

- **iOS**: 12.0+
- **Xcode**: 13.0+
- **Swift**: 5.0+
- **CocoaPods**: Installed (`sudo gem install cocoapods`)

---

## Step 1: Setup Xcode Project

### 1.1 Create Keyboard Extension

1. Open your iOS app project in Xcode
2. **File → New → Target**
3. Select **Custom Keyboard Extension**
4. Name it (e.g., "SmartKeyboard")
5. Click **Finish**

### 1.2 Add Model Files

1. Extract `KeyboardAI-iOS-Package.zip`
2. Drag all files into your keyboard extension target:
   - `tiny_lstm.pt`
   - `tokenizer.model`
   - `tokenizer.vocab`
   - `language_rules.yaml`
   - `custom_dictionary.json`
3. **Important**: Check "Copy items if needed" and add to keyboard extension target

---

## Step 2: Install PyTorch Mobile via CocoaPods

### 2.1 Create/Update Podfile

In your project root, create or update `Podfile`:

```ruby
platform :ios, '12.0'

target 'SmartKeyboard' do
  use_frameworks!
  
  # PyTorch Mobile (Lite Interpreter)
  pod 'LibTorch-Lite', '~> 1.13.0'
end

# Post-install script to fix build issues
post_install do |installer|
  installer.pods_project.targets.each do |target|
    target.build_configurations.each do |config|
      config.build_settings['EXCLUDED_ARCHS[sdk=iphonesimulator*]'] = 'arm64'
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '12.0'
    end
  end
end
```

### 2.2 Install Dependencies

```bash
cd /path/to/your/project
pod install
```

**Important**: From now on, open `YourProject.xcworkspace` (not `.xcodeproj`)

---

## Step 3: Create Objective-C++ Bridge

PyTorch is written in C++, so we need an Objective-C++ wrapper to use it from Swift.

### 3.1 Create TorchBridge.h

**File → New → File → Header File**

Name: `TorchBridge.h`

```objc
#import <Foundation/Foundation.h>

NS_ASSUME_NONNULL_BEGIN

@interface TorchBridge : NSObject

- (nullable instancetype)initWithModelPath:(NSString *)modelPath;
- (nullable NSArray<NSNumber *> *)predictWithInput:(NSArray<NSNumber *> *)input;

@end

NS_ASSUME_NONNULL_END
```

### 3.2 Create TorchBridge.mm

**IMPORTANT**: This MUST be a `.mm` file (Objective-C++), NOT `.m` (Objective-C)!

**Steps**:
1. **File → New → File → Objective-C File**
2. **Name**: `TorchBridge`
3. Xcode will create `TorchBridge.m`
4. **RENAME** `TorchBridge.m` → `TorchBridge.mm` (change extension!)
5. Add this code:

**TorchBridge.mm** (note the `.mm` extension!):

```objc
#import "TorchBridge.h"
#import <torch/script.h>

@implementation TorchBridge {
    torch::jit::script::Module _module;
}

- (nullable instancetype)initWithModelPath:(NSString *)modelPath {
    self = [super init];
    if (self) {
        try {
            // Load the model
            _module = torch::jit::load([modelPath UTF8String]);
            _module.eval();
        } catch (const std::exception& e) {
            NSLog(@"Error loading model: %s", e.what());
            return nil;
        }
    }
    return self;
}

- (nullable NSArray<NSNumber *> *)predictWithInput:(NSArray<NSNumber *> *)input {
    try {
        // Convert NSArray to std::vector
        std::vector<int64_t> inputVec;
        inputVec.reserve([input count]);
        for (NSNumber *num in input) {
            inputVec.push_back([num longLongValue]);
        }
        
        // Create tensor [1, seq_length]
        auto options = torch::TensorOptions().dtype(torch::kLong);
        auto inputTensor = torch::from_blob(
            inputVec.data(),
            {1, static_cast<long>(inputVec.size())},
            options
        ).clone();
        
        // Run inference
        std::vector<torch::jit::IValue> inputs;
        inputs.push_back(inputTensor);
        
        auto output = _module.forward(inputs).toTuple()->elements[0].toTensor();
        
        // Get last token's logits [vocab_size]
        auto lastLogits = output[0][-1];
        auto logitsAccessor = lastLogits.accessor<float, 1>();
        
        // Convert to NSArray
        NSMutableArray *result = [NSMutableArray array];
        for (int i = 0; i < lastLogits.size(0); i++) {
            [result addObject:@(logitsAccessor[i])];
        }
        
        return result;
        
    } catch (const std::exception& e) {
        NSLog(@"Error during inference: %s", e.what());
        return nil;
    }
}

@end
```

### 3.3 Create Bridging Header

If Xcode doesn't create it automatically:

**File → New → File → Header File**

Name: `YourProject-Bridging-Header.h`

```objc
#import "TorchBridge.h"
```

**Build Settings → Swift Compiler - General → Objective-C Bridging Header**:
Set to: `YourProject-Bridging-Header.h`

---

## Step 4: Create Swift Wrapper

### 4.1 Create KeyboardAIModel.swift

```swift
import Foundation

class KeyboardAIModel {
    private let torchBridge: TorchBridge
    private let tokenizer: Tokenizer
    private let vocabSize: Int
    
    init?() {
        // Get model path
        guard let modelPath = Bundle.main.path(forResource: "tiny_lstm", ofType: "pt") else {
            print("Model file not found")
            return nil
        }
        
        // Initialize PyTorch bridge
        guard let bridge = TorchBridge(modelPath: modelPath) else {
            print("Failed to load PyTorch model")
            return nil
        }
        self.torchBridge = bridge
        
        // Initialize tokenizer
        guard let tokenizer = Tokenizer() else {
            print("Failed to load tokenizer")
            return nil
        }
        self.tokenizer = tokenizer
        self.vocabSize = tokenizer.vocabSize
    }
    
    func predict(text: String, topK: Int = 5) -> [String] {
        // Tokenize input
        let tokenIds = tokenizer.encode(text)
        guard !tokenIds.isEmpty else { return [] }
        
        // Take last 50 tokens (model's max sequence length)
        let input = Array(tokenIds.suffix(50))
        
        // Convert to NSNumber array
        let inputNumbers = input.map { NSNumber(value: $0) }
        
        // Run inference
        guard let logits = torchBridge.predict(withInput: inputNumbers) else {
            print("Inference failed")
            return []
        }
        
        // Get top-K predictions
        let topIndices = getTopK(logits: logits, k: topK)
        
        // Convert to words
        return topIndices.map { tokenizer.decode([$0]) }
    }
    
    private func getTopK(logits: [NSNumber], k: Int) -> [Int] {
        let scores = logits.enumerated().map { (index: $0, value: $1.floatValue) }
        let sorted = scores.sorted { $0.value > $1.value }
        return Array(sorted.prefix(k).map { $0.index })
    }
}
```

### 4.2 Create Tokenizer.swift

```swift
import Foundation

class Tokenizer {
    private var handle: OpaquePointer?
    let vocabSize: Int
    
    init?() {
        guard let modelPath = Bundle.main.path(forResource: "tokenizer", ofType: "model") else {
            print("Tokenizer model not found")
            return nil
        }
        
        // Load SentencePiece model (you'll need to add SentencePiece library)
        // For now, using a simple implementation
        // In production, use: https://github.com/google/sentencepiece
        
        // Read vocab size from model_info.json
        if let infoPath = Bundle.main.path(forResource: "model_info", ofType: "json"),
           let data = try? Data(contentsOf: URL(fileURLWithPath: infoPath)),
           let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let vocab = json["vocab_size"] as? Int {
            self.vocabSize = vocab
        } else {
            self.vocabSize = 100 // Default
        }
    }
    
    func encode(_ text: String) -> [Int] {
        // Simplified tokenization
        // In production, use SentencePiece C++ library
        let words = text.lowercased().components(separatedBy: .whitespaces)
        return words.map { word in
            // Simple hash-based encoding (replace with SentencePiece)
            abs(word.hashValue % vocabSize)
        }
    }
    
    func decode(_ ids: [Int]) -> String {
        // Simplified decoding
        // In production, use SentencePiece C++ library
        return ids.map { String($0) }.joined(separator: " ")
    }
}
```

---

## Step 5: Integrate into Keyboard

### 5.1 Update KeyboardViewController.swift

```swift
import UIKit

class KeyboardViewController: UIInputViewController {
    
    private var model: KeyboardAIModel?
    private var suggestionBar: UIStackView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Load model
        model = KeyboardAIModel()
        if model == nil {
            print("Failed to initialize model")
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
        guard let model = model else { return }
        
        // Get predictions in background
        DispatchQueue.global(qos: .userInteractive).async { [weak self] in
            let suggestions = model.predict(text: text, topK: 3)
            
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

## Step 6: Build Settings

### 6.1 Enable C++ Standard Library

**Build Settings → Apple Clang - Language - C++**:
- C++ Language Dialect: `GNU++17`
- C++ Standard Library: `libc++`

### 6.2 Other Linker Flags

**Build Settings → Linking → Other Linker Flags**:
Add: `-all_load`

---

## Step 7: Test

### 7.1 Build and Run

1. Select your keyboard extension scheme
2. Build (⌘B)
3. Run on simulator or device
4. **Settings → General → Keyboard → Keyboards → Add New Keyboard**
5. Select your keyboard
6. Test in any app (Messages, Notes, etc.)

### 7.2 Debug

View logs in Xcode console while keyboard is active.

---

## Troubleshooting

### C++ Syntax Errors in TorchBridge

**Error**: `Expected ';' at end of declaration list` or `Use of undeclared identifier 'try'`

**Cause**: Your file is `.m` (Objective-C) instead of `.mm` (Objective-C++)

**Solution**:
1. **Check file extension** in Xcode Project Navigator
2. If it shows `TorchBridge.m`, **rename it**:
   - Right-click on `TorchBridge.m`
   - Select **Rename**
   - Change to `TorchBridge.mm`
3. **Clean and rebuild**:
   - Product → Clean Build Folder (⇧⌘K)
   - Product → Build (⌘B)

**Why**: 
- `.m` = Objective-C (no C++ support)
- `.mm` = Objective-C++ (supports C++ features like `try/catch`, `std::vector`, etc.)
- PyTorch is C++, so we need `.mm`

---

### LibTorch API Errors

**Error**: `No member named '_load_for_mobile' in namespace 'torch::jit'`

**Solution**: Use `torch::jit::load()` instead:
```objc
// ❌ Wrong (mobile-specific, not in all versions)
_module = torch::jit::_load_for_mobile([modelPath UTF8String]);

// ✅ Correct (standard API)
_module = torch::jit::load([modelPath UTF8String]);
```

**Error**: `No matching function for call to 'from_blob'`

**Solution**: Use `TensorOptions` to specify dtype:
```objc
// ❌ Wrong (missing dtype specification)
auto inputTensor = torch::from_blob(
    inputVec.data(),
    {1, (long)inputVec.size()},
    torch::kLong
).clone();

// ✅ Correct (with TensorOptions)
auto options = torch::TensorOptions().dtype(torch::kLong);
auto inputTensor = torch::from_blob(
    inputVec.data(),
    {1, static_cast<long>(inputVec.size())},
    options
).clone();
```

**Also change module type**:
```objc
// ❌ Wrong
torch::jit::mobile::Module _module;

// ✅ Correct
torch::jit::script::Module _module;
```

---

### Import Header Not Found

**Error**: `'torch/script.h' file not found` or `'LibTorch-Lite/Libtorch.h' file not found`

**Solution**:
1. **Verify CocoaPods installation**:
   ```bash
   cd /path/to/project
   pod install
   ```

2. **Open workspace, not project**:
   - Always use `YourProject.xcworkspace`
   - NOT `YourProject.xcodeproj`

3. **Use correct import**:
   ```objc
   #import <torch/script.h>  // ✅ Correct
   // NOT: #import <LibTorch-Lite/Libtorch.h>  // ❌ Wrong
   ```

4. **Check Header Search Paths**:
   - Build Settings → Search Paths → Header Search Paths
   - Should include: `${PODS_ROOT}/LibTorch-Lite/install/include`
   - This is usually added automatically by CocoaPods

5. **Clean and rebuild**:
   - Product → Clean Build Folder (⇧⌘K)
   - Product → Build (⌘B)

### Model Not Loading

**Error**: "Model file not found"

**Solution**:
- Verify `tiny_lstm.pt` is in keyboard extension target
- Check Bundle Resources in Build Phases

### Linker Errors

**Error**: "Undefined symbols for architecture arm64"

**Solution**:
- Add `-all_load` to Other Linker Flags
- Verify LibTorch-Lite is in Podfile

### Memory Issues

**Error**: Keyboard crashes or is killed

**Solution**:
- iOS limits keyboard extensions to ~30MB memory
- Model + tokenizer (~700KB) should be fine
- Implement caching carefully
- Release resources when not in use

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

---

## Next Steps

1. ✅ Test on physical device
2. ✅ Measure prediction latency (should be <50ms)
3. ✅ Monitor memory usage
4. ✅ Collect real training data and retrain
5. ✅ Submit to App Store

---

## Resources

- [PyTorch Mobile iOS Docs](https://pytorch.org/mobile/ios/)
- [LibTorch CocoaPods](https://cocoapods.org/pods/LibTorch-Lite)
- [iOS Keyboard Extension Guide](https://developer.apple.com/documentation/uikit/keyboards_and_input/creating_a_custom_keyboard)
