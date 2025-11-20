"""
Evaluate Phase 1 Merged Model: 5 Categories
Date: 2025-11-05 10:24:52 UTC
User: Manishnm10

Evaluates: models/phase1_5cat_best.h5
Categories: acne, dermatitis, psoriasis, ringworm, urticaria
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import json
import os

print("\n" + "="*70)
print("📊 PHASE 1 MERGED MODEL EVALUATION (5 CATEGORIES)")
print("="*70)
print(f"⏰ Time: 2025-11-05 10:24:52 UTC")
print(f"👤 User: Manishnm10")

# Load model
print("\n🔍 Loading model...")
try:
    model = keras.models.load_model('models/phase1_5cat_best.h5')
    print("✅ Model loaded: models/phase1_5cat_best.h5")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit(1)

# Load class indices
try:
    with open('models/class_indices_phase1_5cat.json', 'r') as f:
        class_indices = json.load(f)
    print("✅ Class indices loaded")
except Exception as e:
    print(f"❌ Error loading class indices: {e}")
    exit(1)

class_names = list(class_indices.keys())
print(f"\n📋 Classes ({len(class_names)}):")
for idx, name in enumerate(class_names):
    marker = " ⭐ MERGED" if name == 'dermatitis' else ""
    print(f"   {idx}. {name}{marker}")

# Prepare validation data
print("\n📊 Loading validation data...")
val_datagen = ImageDataGenerator(rescale=1./255)

try:
    validation_generator = val_datagen.flow_from_directory(
        'data/skin_diseases_phase1_5cat_merged/validation',
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical',
        shuffle=False
    )
    print(f"✅ Validation samples: {validation_generator.samples}")
except Exception as e:
    print(f"❌ Error loading validation data: {e}")
    exit(1)

# Get predictions
print("\n🔮 Making predictions...")
predictions = model.predict(validation_generator, verbose=1)
y_pred = np.argmax(predictions, axis=1)
y_true = validation_generator.classes

# Classification Report
print("\n" + "="*70)
print("📊 DETAILED CLASSIFICATION REPORT")
print("="*70)
report = classification_report(y_true, y_pred, target_names=class_names, digits=4)
print(report)

# Confusion Matrix
print("\n" + "="*70)
print("🔢 CONFUSION MATRIX")
print("="*70)
cm = confusion_matrix(y_true, y_pred)

print(f"\n{'True ↓ / Pred →':<20s}", end='')
for name in class_names:
    print(f"{name[:10]:>12s}", end='')
print()
print("-" * 85)

for i, name in enumerate(class_names):
    print(f"{name:<20s}", end='')
    for j in range(len(class_names)):
        if i == j:
            print(f"{cm[i][j]:>12d}", end='')  # Diagonal (correct)
        else:
            print(f"{cm[i][j]:>12d}", end='')  # Off-diagonal (errors)
    print()

# Per-class accuracy with detailed analysis
print("\n" + "="*70)
print("📈 PER-CLASS PERFORMANCE ANALYSIS")
print("="*70)
print(f"{'Category':<20} {'Images':<10} {'Correct':<10} {'Accuracy':<12} {'Status'}")
print("-"*75)

category_stats = []
for i, class_name in enumerate(class_names):
    class_correct = cm[i, i]
    class_total = cm[i].sum()
    class_accuracy = (class_correct / class_total) * 100 if class_total > 0 else 0
    
    # Status indicator
    if class_accuracy >= 75:
        status = "✅ Excellent"
    elif class_accuracy >= 65:
        status = "✅ Good"
    elif class_accuracy >= 55:
        status = "⚠️  Fair"
    elif class_accuracy >= 45:
        status = "⚠️  Poor"
    else:
        status = "❌ Very Poor"
    
    category_stats.append({
        'name': class_name,
        'total': class_total,
        'correct': class_correct,
        'accuracy': class_accuracy
    })
    
    marker = " ⭐" if class_name == 'dermatitis' else ""
    print(f"{class_name:<20} {class_total:<10} {class_correct:<10} {class_accuracy:>8.2f}%   {status}{marker}")

# Overall statistics
total_correct = np.trace(cm)
total_samples = cm.sum()
overall_accuracy = (total_correct / total_samples) * 100

print("-"*75)
print(f"{'OVERALL':<20} {total_samples:<10} {total_correct:<10} {overall_accuracy:>8.2f}%")

# Compare to 7-category original
print("\n" + "="*70)
print("📊 COMPARISON: 7-CAT vs 5-CAT MERGED")
print("="*70)
print(f"\n{'Metric':<30} {'7-Cat Original':<20} {'5-Cat Merged':<20}")
print("-"*75)
print(f"{'Categories':<30} {'7':<20} {'5':<20}")
print(f"{'Overall Accuracy':<30} {'62.14%':<20} {f'{overall_accuracy:.2f}%':<20}")
print(f"{'Improvement':<30} {'-':<20} {f'+{overall_accuracy - 62.14:.2f}%':<20}")

# Dermatitis merge analysis
print("\n" + "="*70)
print("⭐ DERMATITIS MERGE ANALYSIS")
print("="*70)
print("\nOLD (7 categories - separate):")
print("  - Eczema:              66% accuracy, 247 validation samples")
print("  - Atopic Dermatitis:   66% accuracy, 98 validation samples")
print("  - Contact Dermatitis:  31% accuracy, 52 validation samples")
print("  - AVERAGE:             ~54.3% (weighted)")

derm_idx = class_names.index('dermatitis')
derm_accuracy = category_stats[derm_idx]['accuracy']
print(f"\nNEW (5 categories - merged):")
print(f"  - Dermatitis:          {derm_accuracy:.2f}% accuracy, {category_stats[derm_idx]['total']} validation samples")
print(f"  - IMPROVEMENT:         {'+' if derm_accuracy > 54.3 else ''}{derm_accuracy - 54.3:.2f}% 🎉")

# Most confused pairs
print("\n" + "="*70)
print("🔀 MOST CONFUSED CATEGORY PAIRS (Top 10)")
print("="*70)

confused_pairs = []
for i in range(len(class_names)):
    for j in range(len(class_names)):
        if i != j and cm[i, j] > 0:
            confused_pairs.append((class_names[i], class_names[j], cm[i, j]))

confused_pairs.sort(key=lambda x: x[2], reverse=True)

print(f"{'True Class':<20} {'Predicted As':<20} {'Count':<10} {'% of True'}")
print("-"*70)
for true_class, pred_class, count in confused_pairs[:10]:
    true_idx = class_names.index(true_class)
    total_true = cm[true_idx].sum()
    percent = (count / total_true) * 100 if total_true > 0 else 0
    print(f"{true_class:<20} {pred_class:<20} {count:<10} {percent:>6.1f}%")

# Prediction confidence analysis
print("\n" + "="*70)
print("🎯 PREDICTION CONFIDENCE ANALYSIS")
print("="*70)

confidences = np.max(predictions, axis=1)
avg_confidence = np.mean(confidences) * 100
correct_mask = (y_pred == y_true)
avg_conf_correct = np.mean(confidences[correct_mask]) * 100
avg_conf_wrong = np.mean(confidences[~correct_mask]) * 100 if (~correct_mask).any() else 0

print(f"\nAverage confidence (all predictions):    {avg_confidence:.2f}%")
print(f"Average confidence (correct predictions): {avg_conf_correct:.2f}%")
print(f"Average confidence (wrong predictions):   {avg_conf_wrong:.2f}%")
print(f"Confidence difference:                    {avg_conf_correct - avg_conf_wrong:.2f}%")

# Low confidence predictions
low_conf_threshold = 50
low_conf_count = np.sum(confidences * 100 < low_conf_threshold)
print(f"\nLow confidence predictions (<{low_conf_threshold}%): {low_conf_count} ({low_conf_count/len(confidences)*100:.1f}%)")

# Top-2 accuracy
top_2_pred = np.argsort(predictions, axis=1)[:, -2:]
top_2_correct = np.any(top_2_pred == y_true[:, np.newaxis], axis=1).sum()
top_2_accuracy = (top_2_correct / len(y_true)) * 100

print(f"\n✅ Top-2 Accuracy: {top_2_accuracy:.2f}%")
print(f"   (Model's second guess is correct {top_2_accuracy:.1f}% of time)")

# Visualize confusion matrix
try:
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, 
                yticklabels=class_names,
                cbar_kws={'label': 'Count'})
    plt.title('Confusion Matrix - Phase 1 Merged (5 Categories)', fontsize=14, fontweight='bold')
    plt.ylabel('True Label', fontsize=11)
    plt.xlabel('Predicted Label', fontsize=11)
    plt.tight_layout()
    plt.savefig('logs/confusion_matrix_phase1_5cat.png', dpi=300, bbox_inches='tight')
    print(f"\n💾 Confusion matrix saved: logs/confusion_matrix_phase1_5cat.png")
except Exception as e:
    print(f"\n⚠️  Could not save confusion matrix image: {e}")

# Summary and recommendations
print("\n" + "="*70)
print("📝 EVALUATION SUMMARY")
print("="*70)
print(f"\n✅ Overall Accuracy:        {overall_accuracy:.2f}%")
print(f"✅ Top-2 Accuracy:          {top_2_accuracy:.2f}%")
print(f"✅ Average Confidence:      {avg_confidence:.2f}%")
print(f"📊 Total Samples:           {total_samples}")
print(f"✅ Correct Predictions:     {total_correct}")
print(f"❌ Wrong Predictions:       {total_samples - total_correct}")

print("\n" + "="*70)
print("💡 RECOMMENDATIONS")
print("="*70)

# Find weakest categories
weak_categories = [cat for cat in category_stats if cat['accuracy'] < 55]
if weak_categories:
    print("\n⚠️  WEAK CATEGORIES (Need improvement):")
    for cat in weak_categories:
        print(f"   - {cat['name']}: {cat['accuracy']:.1f}% ({cat['total']} samples)")
        if cat['total'] < 300:
            print(f"     → Need more training data (current: {cat['total']}, recommended: 500+)")

# Find strong categories
strong_categories = [cat for cat in category_stats if cat['accuracy'] >= 75]
if strong_categories:
    print("\n✅ STRONG CATEGORIES (Excellent performance):")
    for cat in strong_categories:
        print(f"   - {cat['name']}: {cat['accuracy']:.1f}%")

good_categories = [cat for cat in category_stats if 65 <= cat['accuracy'] < 75]
if good_categories:
    print("\n✅ GOOD CATEGORIES (Solid performance):")
    for cat in good_categories:
        print(f"   - {cat['name']}: {cat['accuracy']:.1f}%")

print("\n" + "="*70)
print("🎯 NEXT STEPS")
print("="*70)

if overall_accuracy >= 68:
    print("\n✅ Model performs well! Ready for deployment.")
    print("   Actions:")
    print("   1. Deploy to production")
    print("   2. Monitor real-world performance")
    print("   3. Consider Phase 2 (add more categories)")
elif overall_accuracy >= 62:
    print("\n⚠️  Model is acceptable but could be better.")
    print("   Options:")
    print("   1. Deploy as-is for testing")
    print("   2. Collect more data for weak categories")
    print("   3. Try different model architecture")
    print("   4. Consider merging similar weak categories")
else:
    print("\n❌ Model needs significant improvement.")
    print("   Recommendations:")
    print("   1. Collect much more training data")
    print("   2. Try advanced architectures (EfficientNet, ResNet)")
    print("   3. Review data quality and labeling")
    print("   4. Consider reducing categories further")

# Merge suggestions
if overall_accuracy < 65:
    print("\n💡 MERGE SUGGESTIONS:")
    print("   Consider merging:")
    weak_pairs = []
    if 'psoriasis' in [c['name'] for c in weak_categories] and 'ringworm' in [c['name'] for c in weak_categories]:
        print("   - Psoriasis + Ringworm → 'Scaly Skin Conditions'")
        print("     (Both show scaling and patches)")

print("\n" + "="*70)
print("✅ EVALUATION COMPLETE!")
print("="*70)
print(f"\n📁 Results:")
print(f"   - Console output (detailed metrics)")
print(f"   - logs/confusion_matrix_phase1_5cat.png")
print(f"🎯 Model: models/phase1_5cat_best.h5")
print(f"📊 Accuracy: {overall_accuracy:.2f}% (vs 62.14% original)")
print(f"⏰ Evaluated: 2025-11-05 10:24:52 UTC")

# Final verdict
print("\n" + "="*70)
print("🏁 FINAL VERDICT")
print("="*70)

if overall_accuracy > 62.14:
    improvement = overall_accuracy - 62.14
    print(f"\n🎉 SUCCESS! Model improved by {improvement:.2f}%")
    print(f"   Original (7 cat): 62.14%")
    print(f"   Merged (5 cat):   {overall_accuracy:.2f}%")
    if improvement >= 5:
        print(f"   Status: SIGNIFICANT IMPROVEMENT ✅✅")
    elif improvement >= 2:
        print(f"   Status: GOOD IMPROVEMENT ✅")
    else:
        print(f"   Status: SLIGHT IMPROVEMENT ✅")
elif overall_accuracy == 62.14:
    print(f"\n⚠️  Model performance unchanged at {overall_accuracy:.2f}%")
    print(f"   Merge simplified model but accuracy same")
    print(f"   Benefit: Cleaner 5-category system")
else:
    decline = 62.14 - overall_accuracy
    print(f"\n⚠️  Model accuracy declined by {decline:.2f}%")
    print(f"   Original (7 cat): 62.14%")
    print(f"   Merged (5 cat):   {overall_accuracy:.2f}%")
    print(f"   May need to revisit merge strategy")

print("\n" + "="*70)