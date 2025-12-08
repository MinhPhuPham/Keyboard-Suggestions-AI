# On-Device Multilingual Next-Word Prediction with Custom Dictionaries & Rules

*For iOS/Android Keyboard Extensions — Text Only*

**Goal:** A tiny (< 30  MB), offline, multilingual text suggestion engine that supports Unicode, symbols, emoji, custom user dictionaries, language-specific rules, and dynamic language switching — all within mobile keyboard extension constraints.

---

## ✅ 1. Enhanced Core Requirements

| Feature | Specification |
|---------|---------------|
| **Input** | Unicode text (including emoji 🎉, symbols ©, CJK, Latin, etc.) |
| **Languages** | English + Japanese now; architecture ready for 3–5+ languages |
| **Language Switching** | Auto-detect or let user select active language(s) per session |
| **Custom Dictionaries** | User-defined key-value mappings (e.g., "acxa" → "scackscac") |
| **Training Rules** | Per-language config: grammar style, teen slang, formality, emoji frequency |
| **"No Mean" Filter** | Suppress random chars, spam, low-coherence sequences (callback function: (No-mean prevention callback)) |
| **Platform** | iOS + Android (separate build scripts, shared core logic) |
| **Model Size** | ≤ 5 MB total (including tokenizer, rules, custom dict cache) |
| **Real-Time Update** | Support hot-reload of custom dictionaries (no app restart) |

---

## ✅ 2. System Architecture

```
User Input → Tokenizer → Language Detector → Custom Dictionary Lookup
                                                         ↓
                                              [Prefix Match Found?]
                                                    ↙        ↘
                                                  YES        NO
                                                   ↓          ↓
                                          Return Custom  → TinyLSTM
                                                             ↓
                                                    Apply Rules Filter
                                                             ↓
                                                    "No Mean" Filter
                                                             ↓
                                                    Top-N Suggestions (N number configurable)
```

**🔑 Key Insight:** Custom dictionaries are not part of the neural model — they are fast prefix-lookup tables that override or augment model output.

---

## ✅ 3. Unicode, Emoji & Symbol Support

**Strategy:**

- **Include emoji/symbols in training data:**
  - Scrape public datasets with emoji (e.g., Twitter, messaging logs)
  - Add synthetic examples: "I love you ❤️", "Check this out! 👀"

- **Tokenizer training:**
  - SentencePiece natively supports Unicode
  - Set `--character_coverage=1.0` to preserve rare symbols/emoji
  - Reserve top 256 tokens for most frequent emoji/symbols

- **Model output:**
  - Emoji treated as normal tokens → can be predicted after "I'm happy"

**✅ Result:** Typing "I'm happy " → suggests ["😊", "🥰", "today"]

---

## ✅ 4. Multilingual Architecture (Scalable)

**Language Management:**

- **Active languages:** Configurable via UI (e.g., [EN], [JA], or [EN, JA])
- **Per-language assets:**

```
models/
├── tokenizer.model          # Shared SentencePiece (EN+JA+emoji)
├── tiny_lstm.tflite         # Shared weights
└── rules/
    ├── en/
    │   ├── rules.json       # English-specific rules
    │   └── blocklist.txt
    └── ja/
        ├── rules.json       # Japanese-specific rules
        └── blocklist.txt
```

**Language Switching Logic:**

- If user selects **EN only** → model runs in English context
- If **JA only** → Japanese context
- If **mixed** → tokenizer handles seamlessly; model uses shared weights

**🔁 No separate models per language** → saves space, enables code-switching

---

## ✅ 5. Custom Dictionary System (User-Defined Mappings)

**Design:**

- **Storage:** SQLite DB or key-sorted JSON (for fast prefix search)
- **Format:** `(prefix_key: String, full_value: String)`
  - Example: `("acxa", "scackscac")`
- **Lookup:** On every keystroke, check if current input matches prefix of any custom key
- **Priority:** Custom matches rank above model suggestions

**Update Flow:**

- User adds/removes via app settings
- Dictionary reloaded in < 50 ms (no keyboard restart)
- Synced across devices via iCloud / Google Drive (optional)

**Integration with Model:**

- **Not trained into neural net** → avoids retraining
- **Injected at inference time:**

```swift
func getSuggestions(input: String) -> [String] {
    let customMatches = customDict.prefixSearch(input)  // Fast O(log n)
    let modelSuggestions = model.predict(input)
    return customMatches + modelSuggestions.filter { !customMatches.contains($0) }
}
```

**✅ Handles:** "ac" → ["scackscac", "account", "action"]

---

## ✅ 6. Language-Specific Training Rules

Each language has a `rules.json`:

**English (`en/rules.json`):**

```json
{
  "allow_teen_slang": true,
  "formality": "casual",
  "emoji_frequency": "high",
  "grammar_style": "relaxed",
  "boost_tokens": ["gonna", "wanna", "lol", "😂"]
}
```

**Japanese (`ja/rules.json`):**

```json
{
  "allow_teen_slang": false,
  "formality": "polite",
  "emoji_frequency": "low",
  "grammar_style": "formal",
  "boost_tokens": ["です", "ます", "ございます"]
}
```

**Rule Application:**

- **During training:** Augment data with rule-compliant examples
- **During inference:** Adjust logits (e.g., boost "gonna" if `allow_teen_slang=true`)

---

## ✅ 7. Model & Tokenizer Specs

| Component | Details |
|-----------|---------|
| **Model** | TinyLSTM (64-dim embed, 128-dim hidden, 1 layer) |
| **Vocab Size** | 25,000 (covers EN, JA, emoji, symbols) |
| **Tokenizer** | SentencePiece (Unigram, character_coverage=1.0) |
| **Quantization** | INT8 (via TensorFlow Lite / Core ML) |
| **Model Size** | ~100 KB |
| **Tokenizer Size** | ~900 KB |
| **Total Core** | ~1.1 MB |

---

## ✅ 8. Platform-Specific Build System

**Shared Core (C++17)**

- Model inference
- SentencePiece tokenizer (C++ API)
- Dictionary prefix search (trie-based)
- Rule engine

**iOS Build Script (`build_ios.sh`)**

```bash
#!/bin/bash
clang++ -std=c++17 -O3 -arch arm64 \
  -framework CoreML \
  -I sentencepiece/src \
  -o libkeyboard_core.dylib \
  core/*.cpp sentencepiece.a
codesign --force --sign - libkeyboard_core.dylib
```

**Android Build Script (`build_android.sh`)**

```bash
#!/bin/bash
$NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64/bin/clang++ \
  -std=c++17 -O3 -march=armv8-a \
  -I sentencepiece/src \
  -shared -o libkeyboard_core.so \
  core/*.cpp sentencepiece.a
```

**✅ Same C++ core, two thin platform wrappers**

---

## ✅ 9. Final Asset Breakdown

| Component | Size |
|-----------|------|
| Quantized TinyLSTM | 100 KB |
| SentencePiece tokenizer (EN+JA+emoji) | 900 KB |
| Language rules (en/, ja/) | 50 KB |
| Blocklists / allowlists | 100 KB |
| Custom dictionary engine (trie + loader) | 200 KB |
| **Total** | **~1.4 MB ✅** |

**🎯 Leaves >3.5 MB headroom for future languages or larger vocab.**

---

## ✅ 10. Development Roadmap

| Phase | Tasks |
|-------|-------|
| **1. Data & Tokenizer** | Collect EN+JA+emoji data → train SentencePiece with full Unicode |
| **2. Model Training** | Train TinyLSTM with rule-aware data augmentation |
| **3. Custom Dictionary** | Build prefix-trie + hot-reload system (C++) |
| **4. Rule Engine** | Implement per-language JSON rules + inference-time biasing |
| **5. No-Mean Filter** | Add entropy/confidence threshold to suppress junk |
| **6. iOS Integration** | Core ML + C++ wrapper + keyboard extension |
| **7. Android Integration** | TFLite + JNI + keyboard service |
| **8. Testing** | Validate: "ac" → "scackscac", "今日は" → natural JA, "spam123" → no output |

---

## ✅ 11. Example User Flows

| Scenario | Behavior |
|----------|----------|
| User types "ac" (EN mode) | Returns ["scackscac", "account", "action"] (custom first) |
| User types "今日は" (JA mode) | Returns ["いい", "晴れ", "ですね"] (polite form, no teen slang) |
| User types "xdxd123" | Returns no suggestions (detected as "no mean") |
| User adds new mapping: "ty" → "thank you" | Next "ty" → ["thank you", "type", ...] instantly |
| Switch to JA+EN mode | Supports code-switching: "東京 is" → ["great", "awesome", "最高"] |

---

**End of Specification**