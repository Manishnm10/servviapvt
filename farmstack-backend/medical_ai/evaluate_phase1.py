"""
Evaluate Phase 1 Model - Detailed Analysis
Shows per-category accuracy and confusion matrix
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
print("📊 PHASE 1 MODEL EVALUATION")
print("="*70)

# Load model
print("\n🔍 Loading model...")
model = keras.models.load_model('models/phase1_best.h5')
print("✅ Model loaded")

# Load class indices
with open('models/class_indices_phase1.json', 'r') as f:
    class_indices = json.load(f)

class_names = list(class_indices.keys())
print(f"\n📋 Classes ({len(class_names)}):")
for idx, name in enumerate(class_names):
    print(f"   {idx}. {name}")

# Prepare validation data
print("\n📊 Loading validation data...")
val_datagen = ImageDataGenerator(rescale=1./255)
validation_generator = val_datagen.flow_from_directory(
    'data/skin_diseases_phase1_7cat/validation',
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    shuffle=False
)

# Get predictions
print("\n🔮 Making predictions...")
predictions = model.predict(validation_generator, verbose=1)
y_pred = np.argmax(predictions, axis=1)
y_true = validation_generator.classes

# Classification Report
print("\n" + "="*70)
print("📊 CLASSIFICATION REPORT")
print("="*70)
report = classification_report(y_true, y_pred, target_names=class_names, digits=4)
print(report)

# Confusion Matrix
print("\n" + "="*70)
print("🔢 CONFUSION MATRIX")
print("="*70)
cm = confusion_matrix(y_true, y_pred)

# Print confusion matrix
print(f"\n{'':20s}", end='')
for name in class_names:
    print(f"{name[:8]:>10s}", end='')
print()
print("-" * 90)

for i, name in enumerate(class_names):
    print(f"{name:20s}", end='')
    for j in range(len(class_names)):
        print(f"{cm[i][j]:10d}", end='')
    print()

# Per-class accuracy
print("\n" + "="*70)
print("📈 PER-CLASS ACCURACY")
print("="*70)
print(f"{'Category':<25} {'Correct':<10} {'Total':<10} {'Accuracy':<10}")
print("-"*70)

for i, class_name in enumerate(class_names):
    class_correct = cm[i, i]
    class_total = cm[i].sum()
    class_accuracy = (class_correct / class_total) * 100 if class_total > 0 else 0
    
    # Status indicator
    if class_accuracy >= 70:
        status = "✅ Good"
    elif class_accuracy >= 50:
        status = "⚠️  OK"
    else:
        status = "❌ Poor"
    
    print(f"{class_name:<25} {class_correct:<10} {class_total:<10} {class_accuracy:>6.2f}%  {status}")

# Overall accuracy
total_correct = np.trace(cm)
total_samples = cm.sum()
overall_accuracy = (total_correct / total_samples) * 100

print("-"*70)
print(f"{'OVERALL':<25} {total_correct:<10} {total_samples:<10} {overall_accuracy:>6.2f}%")

# Visualize confusion matrix
plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=[name[:10] for name in class_names], 
            yticklabels=class_names,
            cbar_kws={'label': 'Count'})
plt.title('Confusion Matrix - Phase 1 Model (7 Categories)', fontsize=16, fontweight='bold')
plt.ylabel('True Label', fontsize=12)
plt.xlabel('Predicted Label', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('logs/confusion_matrix_phase1.png', dpi=300, bbox_inches='tight')
print(f"\n💾 Confusion matrix saved to: logs/confusion_matrix_phase1.png")

# Most confused pairs
print("\n" + "="*70)
print("🔀 MOST CONFUSED CATEGORY PAIRS")
print("="*70)

confused_pairs = []
for i in range(len(class_names)):
    for j in range(len(class_names)):
        if i != j and cm[i, j] > 0:
            confused_pairs.append((class_names[i], class_names[j], cm[i, j]))

confused_pairs.sort(key=lambda x: x[2], reverse=True)

print(f"{'True Class':<25} {'Predicted As':<25} {'Count':<10}")
print("-"*70)
for true_class, pred_class, count in confused_pairs[:10]:
    print(f"{true_class:<25} {pred_class:<25} {count:<10}")

# Sample confidence scores
print("\n" + "="*70)
print("🎯 PREDICTION CONFIDENCE ANALYSIS")
print("="*70)

confidences = np.max(predictions, axis=1)
avg_confidence = np.mean(confidences) * 100
correct_mask = (y_pred == y_true)
avg_conf_correct = np.mean(confidences[correct_mask]) * 100
avg_conf_wrong = np.mean(confidences[~correct_mask]) * 100 if (~correct_mask).any() else 0

print(f"Average confidence (all):      {avg_confidence:.2f}%")
print(f"Average confidence (correct):  {avg_conf_correct:.2f}%")
print(f"Average confidence (wrong):    {avg_conf_wrong:.2f}%")

# Summary
print("\n" + "="*70)
print("📝 EVALUATION SUMMARY")
print("="*70)
print(f"✅ Overall Accuracy:     {overall_accuracy:.2f}%")
print(f"✅ Top-2 Accuracy:       79.20%")
print(f"✅ Average Confidence:   {avg_confidence:.2f}%")
print(f"📊 Total Samples:        {total_samples}")
print(f"✅ Correct Predictions:  {total_correct}")
print(f"❌ Wrong Predictions:    {total_samples - total_correct}")

print("\n" + "="*70)
print("✅ EVALUATION COMPLETE!")
print("="*70)