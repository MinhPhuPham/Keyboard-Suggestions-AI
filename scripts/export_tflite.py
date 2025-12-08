"""
Export ONNX model to TensorFlow Lite format for Android deployment
"""

import onnx
from onnx_tf.backend import prepare
import tensorflow as tf
from pathlib import Path
import json
import numpy as np


def export_to_tflite(
    onnx_model_path: str,
    output_dir: str = "android/KeyboardAI",
    model_name: str = "keyboard_ai",
    quantize: bool = True
):
    """
    Export ONNX model to TensorFlow Lite format.
    
    Args:
        onnx_model_path: Path to ONNX model
        output_dir: Output directory for TFLite model
        model_name: Name for the TFLite model
        quantize: Whether to apply INT8 quantization
    """
    print("="*70)
    print("Exporting to TensorFlow Lite for Android")
    print("="*70)
    
    # Load ONNX model
    print(f"\n1. Loading ONNX model from: {onnx_model_path}")
    onnx_model = onnx.load(onnx_model_path)
    
    print(f"   ✓ ONNX model loaded")
    
    # Convert ONNX to TensorFlow
    print(f"\n2. Converting ONNX to TensorFlow")
    tf_rep = prepare(onnx_model)
    
    # Export to TensorFlow SavedModel
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    saved_model_dir = output_path / "saved_model"
    tf_rep.export_graph(str(saved_model_dir))
    
    print(f"   ✓ Converted to TensorFlow SavedModel")
    print(f"   Location: {saved_model_dir}")
    
    # Convert to TFLite
    print(f"\n3. Converting to TensorFlow Lite")
    
    converter = tf.lite.TFLiteConverter.from_saved_model(str(saved_model_dir))
    
    if quantize:
        print(f"   Applying INT8 quantization...")
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.int8]
    
    # Convert
    tflite_model = converter.convert()
    
    print(f"   ✓ Converted to TFLite")
    
    # Save TFLite model
    tflite_filename = f"{model_name}_int8.tflite" if quantize else f"{model_name}.tflite"
    tflite_path = output_path / tflite_filename
    
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    
    size_mb = len(tflite_model) / (1024 ** 2)
    
    print(f"\n4. Model saved to: {tflite_path}")
    print(f"   Size: {size_mb:.2f} MB")
    
    # Test the model
    print(f"\n5. Testing TFLite model")
    interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
    interpreter.allocate_tensors()
    
    # Get input/output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    print(f"   Input details:")
    print(f"     Name: {input_details[0]['name']}")
    print(f"     Shape: {input_details[0]['shape']}")
    print(f"     Type: {input_details[0]['dtype']}")
    
    print(f"   Output details:")
    print(f"     Name: {output_details[0]['name']}")
    print(f"     Shape: {output_details[0]['shape']}")
    print(f"     Type: {output_details[0]['dtype']}")
    
    # Test inference
    test_input = np.random.randint(0, 100, size=input_details[0]['shape'], dtype=np.int32)
    interpreter.set_tensor(input_details[0]['index'], test_input)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])
    
    print(f"   ✓ Test inference successful")
    print(f"   Output shape: {output.shape}")
    
    # Save metadata
    metadata = {
        "model_name": model_name,
        "version": "1.0.0",
        "quantized": quantize,
        "model_size_mb": round(size_mb, 2),
        "input_name": input_details[0]['name'],
        "input_shape": input_details[0]['shape'].tolist(),
        "input_dtype": str(input_details[0]['dtype']),
        "output_name": output_details[0]['name'],
        "output_shape": output_details[0]['shape'].tolist(),
        "output_dtype": str(output_details[0]['dtype']),
        "min_android_api": 21
    }
    
    metadata_path = output_path / "model_info.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"   Metadata: {metadata_path}")
    
    print("\n" + "="*70)
    print("✓ TensorFlow Lite export complete!")
    print("="*70)
    print(f"\nFiles created in {output_dir}/:")
    print(f"  - {tflite_filename} (TFLite model)")
    print(f"  - model_info.json (Metadata)")
    
    return str(tflite_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Export model to TFLite")
    parser.add_argument(
        "--model",
        default="models/mobile/tiny_lstm.onnx",
        help="Path to ONNX model"
    )
    parser.add_argument(
        "--output",
        default="android/KeyboardAI",
        help="Output directory"
    )
    parser.add_argument(
        "--name",
        default="keyboard_ai",
        help="Model name"
    )
    parser.add_argument(
        "--no-quantize",
        action="store_true",
        help="Disable INT8 quantization"
    )
    
    args = parser.parse_args()
    
    # Check if model exists
    if not Path(args.model).exists():
        print(f"Error: Model not found: {args.model}")
        print("\nPlease export to ONNX first:")
        print("  python src/utils/export_model.py")
        exit(1)
    
    # Check dependencies
    try:
        import onnx
        import onnx_tf
        import tensorflow as tf
    except ImportError as e:
        print(f"Error: Missing dependency: {e}")
        print("\nInstall with:")
        print("  pip install onnx onnx-tf tensorflow")
        exit(1)
    
    export_to_tflite(
        args.model,
        args.output,
        args.name,
        quantize=not args.no_quantize
    )
