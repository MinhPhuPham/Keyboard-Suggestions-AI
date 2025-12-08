# Android Integration Guide - PyTorch Mobile

Complete step-by-step guide for integrating the KeyboardAI TorchScript model into your Android keyboard app.

---

## Prerequisites

- **Android API**: 21+ (Android 5.0+)
- **Android Studio**: 4.0+
- **Language**: Kotlin or Java
- **Gradle**: 7.0+

---

## Step 1: Setup Android Project

### 1.1 Create Input Method Service

1. Open your Android project in Android Studio
2. **File → New → Service → Service**
3. Name it `KeyboardService`
4. Select "Exported" and "Enabled"

### 1.2 Add Model Files to Assets

1. Extract `KeyboardAI-Android-Package.zip`
2. Copy all files to `app/src/main/assets/`:
   ```
   app/src/main/assets/
   ├── tiny_lstm.pt
   ├── tokenizer.model
   ├── tokenizer.vocab
   ├── language_rules.yaml
   └── custom_dictionary.json
   ```

---

## Step 2: Add PyTorch Mobile Dependencies

### 2.1 Update build.gradle (Project level)

```gradle
buildscript {
    repositories {
        google()
        mavenCentral()
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
```

### 2.2 Update build.gradle (App level)

```gradle
android {
    compileSdk 34
    
    defaultConfig {
        applicationId "com.yourapp.keyboard"
        minSdk 21
        targetSdk 34
        
        ndk {
            abiFilters 'armeabi-v7a', 'arm64-v8a', 'x86', 'x86_64'
        }
    }
    
    buildFeatures {
        viewBinding true
    }
    
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
    
    kotlinOptions {
        jvmTarget = '1.8'
    }
    
    // Prevent compression of model files
    aaptOptions {
        noCompress "pt", "model", "vocab"
    }
}

dependencies {
    // PyTorch Mobile
    implementation 'org.pytorch:pytorch_android_lite:1.13.1'
    implementation 'org.pytorch:pytorch_android_torchvision_lite:1.13.1'
    
    // Kotlin
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    
    // Coroutines for async operations
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'
}
```

### 2.3 Sync Gradle

Click **Sync Now** in Android Studio.

---

## Step 3: Create Model Wrapper (Kotlin)

### 3.1 Create KeyboardAIModel.kt

```kotlin
package com.yourapp.keyboard

import android.content.Context
import org.pytorch.IValue
import org.pytorch.LiteModuleLoader
import org.pytorch.Module
import org.pytorch.Tensor
import java.io.File
import java.io.FileOutputStream

class KeyboardAIModel(private val context: Context) {
    
    private var module: Module? = null
    private val tokenizer: Tokenizer
    private val vocabSize: Int
    
    init {
        // Load model
        val modelPath = assetFilePath(context, "tiny_lstm.pt")
        module = LiteModuleLoader.load(modelPath)
        
        // Load tokenizer
        tokenizer = Tokenizer(context)
        vocabSize = tokenizer.vocabSize
    }
    
    fun predict(text: String, topK: Int = 5): List<String> {
        val module = this.module ?: return emptyList()
        
        try {
            // Tokenize input
            val tokenIds = tokenizer.encode(text)
            if (tokenIds.isEmpty()) return emptyList()
            
            // Take last 50 tokens (model's max sequence length)
            val input = tokenIds.takeLast(50).toLongArray()
            
            // Create tensor [1, seq_length]
            val inputTensor = Tensor.fromBlob(
                input,
                longArrayOf(1, input.size.toLong())
            )
            
            // Run inference
            val outputTuple = module.forward(IValue.from(inputTensor)).toTuple()
            val outputTensor = outputTuple[0].toTensor()
            
            // Get last token's logits [vocab_size]
            val logits = outputTensor.dataAsFloatArray
            val lastTokenLogits = logits.takeLast(vocabSize).toFloatArray()
            
            // Get top-K predictions
            val topIndices = getTopK(lastTokenLogits, topK)
            
            // Convert to words
            return topIndices.map { tokenizer.decode(listOf(it)) }
            
        } catch (e: Exception) {
            e.printStackTrace()
            return emptyList()
        }
    }
    
    private fun getTopK(logits: FloatArray, k: Int): List<Int> {
        return logits.indices
            .sortedByDescending { logits[it] }
            .take(k)
    }
    
    fun close() {
        module?.destroy()
        module = null
    }
    
    companion object {
        /**
         * Copy asset file to internal storage and return path
         */
        fun assetFilePath(context: Context, assetName: String): String {
            val file = File(context.filesDir, assetName)
            
            if (!file.exists()) {
                context.assets.open(assetName).use { input ->
                    FileOutputStream(file).use { output ->
                        input.copyTo(output)
                    }
                }
            }
            
            return file.absolutePath
        }
    }
}
```

### 3.2 Create Tokenizer.kt

```kotlin
package com.yourapp.keyboard

import android.content.Context
import org.json.JSONObject

class Tokenizer(private val context: Context) {
    
    val vocabSize: Int
    
    init {
        // Read vocab size from model_info.json
        vocabSize = try {
            val json = context.assets.open("model_info.json").bufferedReader().use {
                JSONObject(it.readText())
            }
            json.getInt("vocab_size")
        } catch (e: Exception) {
            100 // Default
        }
    }
    
    fun encode(text: String): List<Int> {
        // Simplified tokenization
        // In production, use SentencePiece JNI library
        // See: https://github.com/google/sentencepiece
        
        val words = text.lowercase().split(Regex("\\s+"))
        return words.map { word ->
            // Simple hash-based encoding (replace with SentencePiece)
            Math.abs(word.hashCode() % vocabSize)
        }
    }
    
    fun decode(ids: List<Int>): String {
        // Simplified decoding
        // In production, use SentencePiece JNI library
        return ids.joinToString(" ")
    }
}
```

---

## Step 4: Create Keyboard Service

### 4.1 Create KeyboardService.kt

```kotlin
package com.yourapp.keyboard

import android.inputmethodservice.InputMethodService
import android.view.View
import android.view.inputmethod.EditorInfo
import android.widget.LinearLayout
import android.widget.Button
import kotlinx.coroutines.*

class KeyboardService : InputMethodService() {
    
    private var model: KeyboardAIModel? = null
    private var suggestionBar: LinearLayout? = null
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    override fun onCreate() {
        super.onCreate()
        
        // Load model in background
        scope.launch(Dispatchers.IO) {
            try {
                model = KeyboardAIModel(this@KeyboardService)
                withContext(Dispatchers.Main) {
                    // Model loaded successfully
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
    
    override fun onCreateInputView(): View {
        val view = layoutInflater.inflate(R.layout.keyboard, null)
        suggestionBar = view.findViewById(R.id.suggestion_bar)
        return view
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
        
        if (text.isEmpty()) {
            clearSuggestions()
            return
        }
        
        // Get predictions in background
        scope.launch(Dispatchers.IO) {
            val suggestions = model?.predict(text, topK = 3) ?: emptyList()
            
            withContext(Dispatchers.Main) {
                displaySuggestions(suggestions)
            }
        }
    }
    
    private fun displaySuggestions(suggestions: List<String>) {
        suggestionBar?.removeAllViews()
        
        suggestions.forEach { suggestion ->
            val button = Button(this).apply {
                text = suggestion
                textSize = 16f
                setOnClickListener {
                    currentInputConnection?.commitText(suggestion + " ", 1)
                }
            }
            
            suggestionBar?.addView(button)
        }
    }
    
    private fun clearSuggestions() {
        suggestionBar?.removeAllViews()
    }
    
    override fun onDestroy() {
        model?.close()
        scope.cancel()
        super.onDestroy()
    }
}
```

### 4.2 Create keyboard.xml Layout

**res/layout/keyboard.xml**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:background="#F0F0F0">
    
    <!-- Suggestion Bar -->
    <HorizontalScrollView
        android:layout_width="match_parent"
        android:layout_height="40dp"
        android:background="#FFFFFF"
        android:elevation="2dp">
        
        <LinearLayout
            android:id="@+id/suggestion_bar"
            android:layout_width="wrap_content"
            android:layout_height="match_parent"
            android:orientation="horizontal"
            android:padding="4dp"/>
    </HorizontalScrollView>
    
    <!-- Keyboard Keys (your implementation) -->
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="8dp">
        
        <!-- Add your keyboard layout here -->
        <TextView
            android:layout_width="match_parent"
            android:layout_height="200dp"
            android:gravity="center"
            android:text="Your Keyboard Layout"
            android:textSize="18sp"/>
    </LinearLayout>
    
</LinearLayout>
```

---

## Step 5: Configure AndroidManifest.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.yourapp.keyboard">
    
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.AppCompat">
        
        <!-- Keyboard Service -->
        <service
            android:name=".KeyboardService"
            android:label="@string/keyboard_name"
            android:permission="android.permission.BIND_INPUT_METHOD"
            android:exported="true">
            <intent-filter>
                <action android:name="android.view.InputMethod"/>
            </intent-filter>
            <meta-data
                android:name="android.view.im"
                android:resource="@xml/method"/>
        </service>
        
    </application>
    
</manifest>
```

---

## Step 6: Create Input Method Configuration

**res/xml/method.xml**:

```xml
<?xml version="1.0" encoding="utf-8"?>
<input-method xmlns:android="http://schemas.android.com/apk/res/android"
    android:settingsActivity="com.yourapp.keyboard.SettingsActivity"
    android:supportsSwitchingToNextInputMethod="true"/>
```

---

## Step 7: Build and Test

### 7.1 Build APK

1. **Build → Build Bundle(s) / APK(s) → Build APK(s)**
2. Install on device

### 7.2 Enable Keyboard

1. **Settings → System → Languages & input → Virtual keyboard**
2. **Manage keyboards**
3. Enable your keyboard
4. Test in any app (Messages, Notes, etc.)

### 7.3 Debug

View logs in Android Studio Logcat while keyboard is active.

---

## Troubleshooting

### Model Not Loading

**Error**: "Failed to load model"

**Solution**:
- Verify `tiny_lstm.pt` is in `assets/` folder
- Check `aaptOptions` in build.gradle
- Ensure file isn't compressed

### UnsatisfiedLinkError

**Error**: "couldn't find libc10.so"

**Solution**:
- Add all ABIs to `ndk.abiFilters`
- Clean and rebuild project
- Check PyTorch Mobile version compatibility

### OutOfMemoryError

**Error**: Keyboard crashes with OOM

**Solution**:
- Model + tokenizer (~700KB) should be fine
- Implement prediction caching
- Release model when keyboard is hidden
- Use `android:largeHeap="true"` in manifest (if needed)

---

## Performance Optimization

### 1. Lazy Loading

```kotlin
private val model: KeyboardAIModel by lazy {
    KeyboardAIModel(this)
}
```

### 2. Prediction Caching

```kotlin
private val cache = mutableMapOf<String, List<String>>()

fun getCachedPredictions(text: String): List<String>? {
    return cache[text]
}
```

### 3. Debouncing

```kotlin
private var predictionJob: Job? = null

fun debouncedPredict(text: String) {
    predictionJob?.cancel()
    predictionJob = scope.launch {
        delay(300) // Wait 300ms
        updateSuggestions(text)
    }
}
```

### 4. Use LiteModuleLoader

Already using `LiteModuleLoader` for optimized mobile inference.

---

## Java Version

If using Java instead of Kotlin:

### KeyboardAIModel.java

```java
public class KeyboardAIModel {
    private Module module;
    private Tokenizer tokenizer;
    
    public KeyboardAIModel(Context context) {
        String modelPath = assetFilePath(context, "tiny_lstm.pt");
        module = LiteModuleLoader.load(modelPath);
        tokenizer = new Tokenizer(context);
    }
    
    public List<String> predict(String text, int topK) {
        // Similar implementation as Kotlin version
        // ...
    }
    
    public void close() {
        if (module != null) {
            module.destroy();
            module = null;
        }
    }
}
```

---

## Next Steps

1. ✅ Test on physical device
2. ✅ Measure prediction latency (should be <50ms)
3. ✅ Monitor memory usage
4. ✅ Collect real training data and retrain
5. ✅ Publish to Google Play Store

---

## Resources

- [PyTorch Mobile Android Docs](https://pytorch.org/mobile/android/)
- [PyTorch Android GitHub](https://github.com/pytorch/android-demo-app)
- [Android Input Method Guide](https://developer.android.com/develop/ui/views/touch-and-input/creating-input-method)
- [SentencePiece Android](https://github.com/google/sentencepiece)
