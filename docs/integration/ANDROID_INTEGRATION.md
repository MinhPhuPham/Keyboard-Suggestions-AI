# Android Integration Guide

Complete guide for integrating KeyboardAI into your Android keyboard app.

---

## Package Contents

After running `./scripts/build_android_package.sh`, you'll have:

```
android/KeyboardAI/
├── keyboard_ai_int8.tflite   # TFLite model (quantized)
├── tokenizer.model            # SentencePiece tokenizer
├── tokenizer.vocab            # Vocabulary file
├── language_rules.yaml        # Language rules
├── custom_dictionary.json     # Custom dictionary
├── model_info.json           # Model metadata
└── README.md                 # Package info
```

---

## Requirements

- **Android API**: 21+ (Android 5.0+)
- **Language**: Kotlin or Java
- **Dependencies**:
  - TensorFlow Lite runtime
  - SentencePiece JNI bindings
  - YAML parser (SnakeYAML)
  - JSON parser (Gson or built-in)

---

## Step 1: Add Dependencies

### build.gradle (Module level)

```gradle
dependencies {
    // TensorFlow Lite
    implementation 'org.tensorflow:tensorflow-lite:2.14.0'
    implementation 'org.tensorflow:tensorflow-lite-support:0.4.4'
    
    // SentencePiece (if available, or use JNI)
    // implementation 'com.google.sentencepiece:sentencepiece-android:0.1.0'
    
    // YAML parser
    implementation 'org.yaml:snakeyaml:2.0'
    
    // JSON
    implementation 'com.google.code.gson:gson:2.10.1'
}
```

---

## Step 2: Add Files to Project

### 2.1 Create Assets Folder

```
app/src/main/assets/
├── keyboard_ai_int8.tflite
├── tokenizer.model
├── tokenizer.vocab
├── language_rules.yaml
└── custom_dictionary.json
```

### 2.2 Copy Files

```bash
cp android/KeyboardAI/*.tflite app/src/main/assets/
cp android/KeyboardAI/tokenizer.* app/src/main/assets/
cp android/KeyboardAI/*.yaml app/src/main/assets/
cp android/KeyboardAI/*.json app/src/main/assets/
```

---

## Step 3: Create Kotlin/Java Wrapper Classes

### 3.1 Tokenizer Wrapper (Kotlin)

```kotlin
import android.content.Context
import java.io.File
import java.io.FileOutputStream

class Tokenizer(private val context: Context) {
    private var nativeHandle: Long = 0
    
    init {
        loadModel()
    }
    
    private fun loadModel() {
        // Copy model from assets to internal storage
        val modelFile = File(context.filesDir, "tokenizer.model")
        
        if (!modelFile.exists()) {
            context.assets.open("tokenizer.model").use { input ->
                FileOutputStream(modelFile).use { output ->
                    input.copyTo(output)
                }
            }
        }
        
        // Load with SentencePiece JNI
        nativeHandle = nativeLoad(modelFile.absolutePath)
    }
    
    fun encode(text: String): IntArray {
        return nativeEncode(nativeHandle, text)
    }
    
    fun decode(ids: IntArray): String {
        return nativeDecode(nativeHandle, ids)
    }
    
    fun idToPiece(id: Int): String {
        return nativeIdToPiece(nativeHandle, id)
    }
    
    fun vocabSize(): Int {
        return nativeVocabSize(nativeHandle)
    }
    
    fun close() {
        if (nativeHandle != 0L) {
            nativeUnload(nativeHandle)
            nativeHandle = 0
        }
    }
    
    // Native methods (implement with JNI or use library)
    private external fun nativeLoad(path: String): Long
    private external fun nativeEncode(handle: Long, text: String): IntArray
    private external fun nativeDecode(handle: Long, ids: IntArray): String
    private external fun nativeIdToPiece(handle: Long, id: Int): String
    private external fun nativeVocabSize(handle: Long): Int
    private external fun nativeUnload(handle: Long)
    
    companion object {
        init {
            System.loadLibrary("sentencepiece_jni")
        }
    }
}
```

### 3.2 Model Wrapper (Kotlin)

```kotlin
import android.content.Context
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.support.common.FileUtil
import java.nio.ByteBuffer
import java.nio.ByteOrder

class KeyboardAIModel(context: Context) {
    private val interpreter: Interpreter
    private val tokenizer: Tokenizer
    
    init {
        // Load TFLite model
        val modelBuffer = FileUtil.loadMappedFile(context, "keyboard_ai_int8.tflite")
        
        val options = Interpreter.Options().apply {
            setNumThreads(4)
            setUseNNAPI(true) // Use Android Neural Networks API
        }
        
        interpreter = Interpreter(modelBuffer, options)
        tokenizer = Tokenizer(context)
    }
    
    fun predict(text: String, topK: Int = 5): List<String> {
        // Tokenize input
        val tokenIds = tokenizer.encode(text)
        if (tokenIds.isEmpty()) return emptyList()
        
        // Prepare input tensor
        val inputShape = interpreter.getInputTensor(0).shape()
        val inputBuffer = ByteBuffer.allocateDirect(tokenIds.size * 4).apply {
            order(ByteOrder.nativeOrder())
            tokenIds.forEach { putInt(it) }
            rewind()
        }
        
        // Prepare output tensor
        val outputShape = interpreter.getOutputTensor(0).shape()
        val vocabSize = outputShape[outputShape.size - 1]
        val outputBuffer = ByteBuffer.allocateDirect(vocabSize * 4).apply {
            order(ByteOrder.nativeOrder())
        }
        
        // Run inference
        interpreter.run(inputBuffer, outputBuffer)
        
        // Parse output
        outputBuffer.rewind()
        val logits = FloatArray(vocabSize) {
            outputBuffer.float
        }
        
        // Get top-K predictions
        val topIndices = getTopK(logits, topK)
        
        // Convert to words
        return topIndices.map { tokenizer.idToPiece(it) }
    }
    
    private fun getTopK(logits: FloatArray, k: Int): List<Int> {
        return logits.indices
            .sortedByDescending { logits[it] }
            .take(k)
    }
    
    fun close() {
        interpreter.close()
        tokenizer.close()
    }
}
```

### 3.3 Custom Dictionary (Kotlin)

```kotlin
import android.content.Context
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

data class DictionaryEntry(
    val value: String,
    val priority: Int = 1
)

class CustomDictionary(context: Context) {
    private val entries = mutableMapOf<String, DictionaryEntry>()
    
    init {
        loadDictionary(context)
    }
    
    private fun loadDictionary(context: Context) {
        val json = context.assets.open("custom_dictionary.json")
            .bufferedReader()
            .use { it.readText() }
        
        val gson = Gson()
        val type = object : TypeToken<Map<String, Any>>() {}.type
        val data: Map<String, Any> = gson.fromJson(json, type)
        
        @Suppress("UNCHECKED_CAST")
        val entriesMap = data["entries"] as? Map<String, Map<String, Any>> ?: return
        
        for ((key, value) in entriesMap) {
            val expansion = value["value"] as? String ?: continue
            val priority = (value["priority"] as? Double)?.toInt() ?: 1
            entries[key.lowercase()] = DictionaryEntry(expansion, priority)
        }
    }
    
    fun lookup(prefix: String): List<String> {
        val lowercased = prefix.lowercase()
        return entries
            .filter { it.key.startsWith(lowercased) }
            .sortedByDescending { it.value.priority }
            .map { it.value.value }
    }
    
    fun get(key: String): String? {
        return entries[key.lowercase()]?.value
    }
}
```

### 3.4 Prediction Engine (Kotlin)

```kotlin
import android.content.Context

class PredictionEngine(context: Context) {
    private val model = KeyboardAIModel(context)
    private val dictionary = CustomDictionary(context)
    private val cache = mutableMapOf<String, List<String>>()
    
    fun getSuggestions(text: String, count: Int = 5): List<String> {
        // Check cache
        cache[text]?.let { return it }
        
        val suggestions = mutableListOf<String>()
        
        // 1. Check custom dictionary
        val words = text.split(" ")
        words.lastOrNull()?.let { lastWord ->
            val customMatches = dictionary.lookup(lastWord)
            suggestions.addAll(customMatches)
        }
        
        // 2. Get model predictions
        if (suggestions.size < count) {
            val modelPredictions = model.predict(
                text,
                topK = count - suggestions.size
            )
            
            // Filter duplicates
            modelPredictions.forEach { prediction ->
                if (prediction !in suggestions) {
                    suggestions.add(prediction)
                }
            }
        }
        
        // Cache and return
        val result = suggestions.take(count)
        cache[text] = result
        return result
    }
    
    fun clearCache() {
        cache.clear()
    }
    
    fun close() {
        model.close()
    }
}
```

---

## Step 4: Integrate into Keyboard Service

### 4.1 Create Keyboard Service

```kotlin
import android.inputmethodservice.InputMethodService
import android.view.View
import android.view.inputmethod.EditorInfo
import android.widget.LinearLayout
import android.widget.Button

class KeyboardService : InputMethodService() {
    
    private lateinit var predictionEngine: PredictionEngine
    private lateinit var suggestionBar: LinearLayout
    
    override fun onCreate() {
        super.onCreate()
        predictionEngine = PredictionEngine(this)
    }
    
    override fun onCreateInputView(): View {
        val keyboardView = layoutInflater.inflate(R.layout.keyboard, null)
        suggestionBar = keyboardView.findViewById(R.id.suggestion_bar)
        return keyboardView
    }
    
    override fun onStartInput(attribute: EditorInfo?, restarting: Boolean) {
        super.onStartInput(attribute, restarting)
        updateSuggestions()
    }
    
    override fun onUpdateSelection(
        oldSelStart: Int, oldSelEnd: Int,
        newSelStart: Int, newSelEnd: Int,
        candidatesStart: Int, candidatesEnd: Int
    ) {
        super.onUpdateSelection(
            oldSelStart, oldSelEnd,
            newSelStart, newSelEnd,
            candidatesStart, candidatesEnd
        )
        updateSuggestions()
    }
    
    private fun updateSuggestions() {
        val text = currentInputConnection?.getTextBeforeCursor(100, 0)?.toString()
            ?: return
        
        // Get suggestions in background
        Thread {
            val suggestions = predictionEngine.getSuggestions(text)
            
            runOnUiThread {
                displaySuggestions(suggestions)
            }
        }.start()
    }
    
    private fun displaySuggestions(suggestions: List<String>) {
        suggestionBar.removeAllViews()
        
        suggestions.forEach { suggestion ->
            val button = Button(this).apply {
                text = suggestion
                setOnClickListener {
                    currentInputConnection?.commitText(suggestion, 1)
                }
            }
            suggestionBar.addView(button)
        }
    }
    
    override fun onDestroy() {
        predictionEngine.close()
        super.onDestroy()
    }
}
```

### 4.2 Keyboard Layout (XML)

```xml
<!-- res/layout/keyboard.xml -->
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">
    
    <!-- Suggestion Bar -->
    <HorizontalScrollView
        android:layout_width="match_parent"
        android:layout_height="40dp"
        android:background="#F0F0F0">
        
        <LinearLayout
            android:id="@+id/suggestion_bar"
            android:layout_width="wrap_content"
            android:layout_height="match_parent"
            android:orientation="horizontal"
            android:padding="4dp"/>
    </HorizontalScrollView>
    
    <!-- Keyboard Keys (your implementation) -->
    <!-- ... -->
    
</LinearLayout>
```

### 4.3 AndroidManifest.xml

```xml
<service
    android:name=".KeyboardService"
    android:label="@string/keyboard_name"
    android:permission="android.permission.BIND_INPUT_METHOD">
    <intent-filter>
        <action android:name="android.view.InputMethod"/>
    </intent-filter>
    <meta-data
        android:name="android.view.im"
        android:resource="@xml/method"/>
</service>
```

---

## Step 5: Optimize Performance

### 5.1 Use Coroutines

```kotlin
import kotlinx.coroutines.*

class PredictionEngine(context: Context) {
    private val scope = CoroutineScope(Dispatchers.Default)
    
    fun getSuggestionsAsync(
        text: String,
        callback: (List<String>) -> Unit
    ) {
        scope.launch {
            val suggestions = getSuggestions(text)
            withContext(Dispatchers.Main) {
                callback(suggestions)
            }
        }
    }
}
```

### 5.2 Implement LRU Cache

```kotlin
import android.util.LruCache

class PredictionEngine(context: Context) {
    private val cache = LruCache<String, List<String>>(100) // Cache 100 entries
    
    fun getSuggestions(text: String, count: Int = 5): List<String> {
        cache.get(text)?.let { return it }
        
        // ... compute suggestions ...
        
        cache.put(text, result)
        return result
    }
}
```

### 5.3 Lazy Initialization

```kotlin
class KeyboardService : InputMethodService() {
    private val predictionEngine by lazy {
        PredictionEngine(this)
    }
}
```

---

## Step 6: Memory Management

### 6.1 Monitor Memory

```kotlin
import android.app.ActivityManager
import android.content.Context

fun getMemoryUsage(context: Context): Long {
    val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) 
        as ActivityManager
    val memoryInfo = ActivityManager.MemoryInfo()
    activityManager.getMemoryInfo(memoryInfo)
    
    val runtime = Runtime.getRuntime()
    val usedMemory = runtime.totalMemory() - runtime.freeMemory()
    
    return usedMemory / (1024 * 1024) // MB
}
```

### 6.2 Handle Low Memory

```kotlin
override fun onLowMemory() {
    super.onLowMemory()
    predictionEngine.clearCache()
}
```

---

## Step 7: Testing

### 7.1 Unit Tests

```kotlin
import org.junit.Test
import org.junit.Assert.*

class PredictionEngineTest {
    
    @Test
    fun testPrediction() {
        val engine = PredictionEngine(context)
        val suggestions = engine.getSuggestions("I'm going to")
        
        assertFalse(suggestions.isEmpty())
        assertTrue(suggestions.size <= 5)
    }
    
    @Test
    fun testCustomDictionary() {
        val engine = PredictionEngine(context)
        val suggestions = engine.getSuggestions("ty")
        
        assertTrue(suggestions.contains("thank you"))
    }
    
    @Test
    fun testPerformance() {
        val engine = PredictionEngine(context)
        
        val startTime = System.currentTimeMillis()
        engine.getSuggestions("Hello world")
        val duration = System.currentTimeMillis() - startTime
        
        assertTrue("Prediction took ${duration}ms", duration < 100)
    }
}
```

---

## Performance Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Prediction Latency | < 50ms | Use System.currentTimeMillis() |
| Memory Usage | < 30MB | Use ActivityManager |
| Model Load Time | < 500ms | Measure in onCreate() |
| APK Size Increase | < 5MB | Check APK analyzer |

---

## Troubleshooting

### TFLite Model Not Loading

**Problem**: Model fails to load from assets

**Solutions**:
1. Verify file is in assets folder
2. Check file isn't compressed (add to build.gradle):
   ```gradle
   aaptOptions {
       noCompress "tflite"
   }
   ```
3. Verify model file isn't corrupted

### High Memory Usage

**Problem**: App uses too much memory

**Solutions**:
1. Use INT8 quantized model
2. Implement LRU cache with size limit
3. Close interpreter when not in use
4. Reduce number of threads

### Slow Predictions

**Problem**: Predictions take > 100ms

**Solutions**:
1. Enable NNAPI (`.setUseNNAPI(true)`)
2. Increase thread count
3. Use coroutines for async prediction
4. Implement prediction queue

### SentencePiece JNI Issues

**Problem**: Native library not found

**Solutions**:
1. Build SentencePiece for Android
2. Add .so files to jniLibs folder
3. Or use pure Java tokenizer alternative

---

## Next Steps

1. ✅ Integrate package into your Android project
2. ✅ Test on emulator
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
2. Review logcat output
3. Test with example inputs from test-data/
4. Report performance metrics for optimization
