"""
Evaluate Phase 1 Enhanced Model (5 Categories)
Date: 2025-11-05 19:15:36 UTC
User: Manishnm10

Evaluates the enhanced model trained on 10,426 images
Expected accuracy: 75-78%
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import json
import os
from datetime import datetime
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
MODEL_PATH = 'models/phase1_5cat_enhanced_best.h5'
CLASS_INDICES_PATH = 'models/class_indices_phase1_5cat_enhanced.json'
DATA_DIR = 'data/skin_diseases_phase1_enhanced_5cat'
OUTPUT_DIR = 'evaluation_results'

print("\n" + "="*70)
print("📊 PHASE 1 ENHANCED MODEL EVALUATION (5 CATEGORIES)")
print("="*70)
print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
print(f"👤 User: Manishnm10")

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load model
print("\n🔍 Loading model...")
try:
    model = keras.models.load_model(MODEL_PATH)
    print(f"✅ Model loaded: {MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print(f"\n💡 Make sure training completed and model exists at:")
    print(f"   {MODEL_PATH}")
    exit(1)

# Load class indices
try:
    with open(CLASS_INDICES_PATH, 'r') as f:
        class_indices = json.load(f)
    print(f"✅ Class indices loaded")
except Exception as e:
    print(f"❌ Error loading class indices: {e}")
    exit(1)

# Reverse mapping (index -> class name)
index_to_class = {v: k for k, v in class_indices.items()}

print(f"\n📋 Classes ({len(class_indices)}):")
for idx in sorted(index_to_class.keys()):
    marker = " ⭐ MERGED" if index_to_class[idx] == 'dermatitis' else ""
    print(f"   {idx}. {index_to_class[idx]}{marker}")

# Load validation data
print(f"\n📊 Loading validation data from: {DATA_DIR}/validation")
val_datagen = ImageDataGenerator(rescale=1./255)

try:
    val_gen = val_datagen.flow_from_directory(
        os.path.join(DATA_DIR, 'validation'),
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False  # Important for correct evaluation
    )
    print(f"✅ Loaded {val_gen.samples} validation images")
except Exception as e:
    print(f"❌ Error loading validation data: {e}")
    print(f"\n💡 Expected path: {os.path.join(DATA_DIR, 'validation')}")
    print(f"   Please verify the path exists!")
    exit(1)

# Evaluate
print("\n🔄 Evaluating model on validation set...")
print("   This may take 2-5 minutes...\n")

steps = val_gen.samples // BATCH_SIZE
results = model.evaluate(val_gen, steps=steps, verbose=1)

val_loss = results[0]
val_acc = results[1]
val_top2 = results[2] if len(results) > 2 else None

print("\n" + "="*70)
print("📊 OVERALL RESULTS")
print("="*70)
print(f"   Validation Loss:        {val_loss:.4f}")
print(f"   Validation Accuracy:    {val_acc:.4f} ({val_acc*100:.2f}%)")
if val_top2:
    print(f"   Top-2 Accuracy:         {val_top2:.4f} ({val_top2*100:.2f}%)")

# Get predictions for detailed analysis
print("\n🔄 Generating predictions for detailed analysis...")
val_gen.reset()
predictions = model.predict(val_gen, steps=steps, verbose=1)
predicted_classes = np.argmax(predictions, axis=1)
true_classes = val_gen.classes[:len(predicted_classes)]

# Classification report
print("\n" + "="*70)
print("📊 PER-CATEGORY PERFORMANCE")
print("="*70)

target_names = [index_to_class[i] for i in range(len(class_indices))]
report = classification_report(
    true_classes,
    predicted_classes,
    target_names=target_names,
    digits=4
)
print(report)

# Save classification report
report_dict = classification_report(
    true_classes,
    predicted_classes,
    target_names=target_names,
    output_dict=True
)

# Confusion Matrix
print("\n🔄 Generating confusion matrix...")
cm = confusion_matrix(true_classes, predicted_classes)

# Plot confusion matrix
plt.figure(figsize=(10, 8))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=target_names,
    yticklabels=target_names,
    cbar_kws={'label': 'Count'}
)
plt.title('Confusion Matrix - Phase 1 Enhanced Model (5 Categories)', fontsize=14, fontweight='bold')
plt.ylabel('True Label', fontsize=12)
plt.xlabel('Predicted Label', fontsize=12)
plt.tight_layout()

cm_path = os.path.join(OUTPUT_DIR, 'confusion_matrix_phase1_5cat_enhanced.png')
plt.savefig(cm_path, dpi=300, bbox_inches='tight')
print(f"✅ Confusion matrix saved: {cm_path}")

# Per-category accuracy
print("\n" + "="*70)
print("📊 PER-CATEGORY ACCURACY")
print("="*70)
print(f"{'Category':<20} {'Correct':<10} {'Total':<10} {'Accuracy':<10} {'Status'}")
print("-"*70)

category_stats = {}
for idx in range(len(class_indices)):
    class_name = index_to_class[idx]
    mask = true_classes == idx
    correct = np.sum(predicted_classes[mask] == idx)
    total = np.sum(mask)
    acc = (correct / total * 100) if total > 0 else 0
    
    category_stats[class_name] = {
        'correct': int(correct),
        'total': int(total),
        'accuracy': float(acc)
    }
    
    marker = " ⭐" if class_name == 'dermatitis' else ""
    status = "🎉🎉" if acc >= 80 else ("🎉" if acc >= 70 else ("✅" if acc >= 60 else "⚠️"))
    
    print(f"{class_name:<20} {correct:<10} {total:<10} {acc:>6.2f}%    {status}{marker}")

# Comparison with expectations
print("\n" + "="*70)
print("📊 COMPARISON WITH EXPECTATIONS")
print("="*70)

expectations = {
    'acne': (90, 93),
    'dermatitis': (76, 79),
    'psoriasis': (72, 76),
    'ringworm': (75, 79),
    'urticaria': (73, 77)
}

print(f"{'Category':<20} {'Actual':<12} {'Expected':<15} {'Status'}")
print("-"*65)

for class_name in sorted(category_stats.keys()):
    actual = category_stats[class_name]['accuracy']
    exp_min, exp_max = expectations.get(class_name, (0, 0))
    
    if actual >= exp_min:
        status = "✅ Met/Exceeded"
    elif actual >= exp_min - 5:
        status = "⚠️  Close"
    else:
        status = "❌ Below"
    
    marker = " ⭐" if class_name == 'dermatitis' else ""
    print(f"{class_name:<20} {actual:>6.2f}%     {exp_min}-{exp_max}%        {status}{marker}")

# Overall assessment
print("\n" + "="*70)
print("🎯 OVERALL ASSESSMENT")
print("="*70)

overall_acc = val_acc * 100
improvement_vs_previous = overall_acc - 63.62

print(f"\n📈 Model Performance:")
print(f"   Previous model (5-cat):     63.62%")
print(f"   Enhanced model (current):   {overall_acc:.2f}%")
print(f"   Improvement:                {'+' if improvement_vs_previous > 0 else ''}{improvement_vs_previous:.2f}%")

print(f"\n🎯 Target Achievement:")
if overall_acc >= 75:
    print(f"   ✅✅✅ EXCELLENT! Target (75%) EXCEEDED!")
    print(f"   Status: Production-ready")
elif overall_acc >= 72:
    print(f"   ✅✅ GREAT! Target (72%+) ACHIEVED!")
    print(f"   Status: Production-ready")
elif overall_acc >= 68:
    print(f"   ✅ GOOD! Close to target")
    print(f"   Status: Usable, consider minor improvements")
else:
    print(f"   ⚠️  Below target")
    print(f"   Status: Needs improvement")

# Save evaluation results
eval_results = {
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
    'user': 'Manishnm10',
    'model_path': MODEL_PATH,
    'dataset': DATA_DIR,
    'validation_samples': int(val_gen.samples),
    'overall': {
        'loss': float(val_loss),
        'accuracy': float(val_acc),
        'accuracy_percent': float(overall_acc),
        'top_2_accuracy': float(val_top2) if val_top2 else None
    },
    'per_category': category_stats,
    'classification_report': report_dict,
    'improvement_vs_previous': float(improvement_vs_previous)
}

results_path = os.path.join(OUTPUT_DIR, f'evaluation_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
with open(results_path, 'w') as f:
    json.dump(eval_results, f, indent=4)

print(f"\n💾 Detailed results saved:")
print(f"   JSON:              {results_path}")
print(f"   Confusion Matrix:  {cm_path}")

print("\n" + "="*70)
print("✅ EVALUATION COMPLETE!")
print("="*70)

# Final recommendations
print("\n🎯 RECOMMENDATIONS:")
print("-"*70)
if overall_acc >= 75:
    print("   1. ✅ Model ready for production deployment")
    print("   2. ✅ Create API endpoint for predictions")
    print("   3. ✅ Test with real-world images")
    print("   4. ✅ Monitor performance in production")
elif overall_acc >= 72:
    print("   1. ✅ Model ready for deployment")
    print("   2. ⚠️  Monitor weak categories closely")
    print("   3. 💡 Consider collecting more data for categories <70%")
elif overall_acc >= 68:
    print("   1. ⚠️  Usable but not optimal")
    print("   2. 💡 Collect more data for weak categories")
    print("   3. 💡 Consider EfficientNetB3 architecture")
else:
    print("   1. ⚠️  Review per-category confusion")
    print("   2. ⚠️  Check data quality")
    print("   3. ⚠️  Consider data augmentation improvements")

print("\n🎉 Thank you for using the evaluation tool!")