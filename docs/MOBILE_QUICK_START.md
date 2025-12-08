# Mobile Deployment - Quick Reference

## Build Packages

### All Platforms
```bash
./scripts/build_mobile_packages.sh
```

### iOS Only
```bash
./scripts/build_ios_package.sh
```

### Android Only  
```bash
./scripts/build_android_package.sh
```

---

## Prerequisites

1. **Train Model**
   ```bash
   python src/model/train.py
   ```

2. **Train Tokenizer**
   ```bash
   python src/tokenizer/train_tokenizer.py
   ```

3. **Install Dependencies**
   ```bash
   pip install coremltools onnx-tf tensorflow
   ```

---

## Package Locations

- **iOS**: `ios/KeyboardAI/` + `ios/KeyboardAI-iOS-Package.zip`
- **Android**: `android/KeyboardAI/` + `android/KeyboardAI-Android-Package.zip`

---

## Integration Guides

- **iOS**: [docs/integration/IOS_INTEGRATION.md](integration/IOS_INTEGRATION.md)
- **Android**: [docs/integration/ANDROID_INTEGRATION.md](integration/ANDROID_INTEGRATION.md)

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Prediction Latency | < 50ms |
| Memory Usage | < 30MB |
| Model Load Time | < 500ms |
| Package Size | < 5MB |

---

## Testing Checklist

After integration:
- [ ] Model loads correctly
- [ ] Predictions work
- [ ] Custom dictionary works
- [ ] Performance meets targets
- [ ] Memory usage acceptable

---

## Report Back

Please provide:
1. **Prediction latency** (average ms)
2. **Memory usage** (MB)
3. **Model load time** (ms)
4. **Any integration issues**
5. **Accuracy feedback**
