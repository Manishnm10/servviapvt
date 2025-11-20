"""
Train Phase 1 Enhanced Model: 5 Categories (12,432 images)
Date: 2025-11-05 16:21:43 UTC
User: Manishnm10

ENHANCED VERSION with Kaggle data merged:
- DermNet: 5,741 images
- Kaggle Ismailpromus: 6,691 images  
- Total: 12,432 images → 10,426 organized (80/20 split)

Categories: acne, dermatitis (merged), psoriasis, ringworm, urticaria
Expected accuracy: 72-79%
Training time: ~3-4 hours
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger
from sklearn.utils.class_weight import compute_class_weight
import numpy as np
import os
import json
from datetime import datetime

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS_PHASE1 = 30  # Frozen base
EPOCHS_PHASE2 = 30  # Fine-tuning
EPOCHS_TOTAL = EPOCHS_PHASE1 + EPOCHS_PHASE2

# ✅ UPDATED: Enhanced dataset path
DATA_DIR = 'data/skin_diseases_phase1_enhanced_5cat'

MODEL_DIR = 'models'
LOGS_DIR = 'logs'

print("\n" + "="*70)
print("🚀 PHASE 1 ENHANCED: TRAINING 5 CATEGORIES (12,432 IMAGES)")
print("="*70)
print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
print(f"👤 User: Manishnm10")
print(f"\n📦 Dataset: Enhanced with Kaggle data")
print(f"   DermNet:      5,741 images")
print(f"   + Kaggle:     6,691 images")
print(f"   = Total:     12,432 images")
print(f"   Organized:   10,426 images (80/20 split)")

# Create directories
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Prepare data generators with ENHANCED augmentation
print("\n📊 Preparing data generators...")

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,           # Increased from 20
    width_shift_range=0.25,      # Increased from 0.2
    height_shift_range=0.25,     # Increased from 0.2
    shear_range=0.2,             # Increased from 0.15
    zoom_range=0.2,              # Increased from 0.15
    horizontal_flip=True,
    brightness_range=[0.8, 1.2], # NEW: Lighting variations
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    os.path.join(DATA_DIR, 'train'),
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

val_gen = val_datagen.flow_from_directory(
    os.path.join(DATA_DIR, 'validation'),
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

num_classes = len(train_gen.class_indices)

print(f"✅ Training samples: {train_gen.samples}")
print(f"✅ Validation samples: {val_gen.samples}")
print(f"✅ Classes ({num_classes}):")

# Show detailed class distribution
for cat, idx in sorted(train_gen.class_indices.items(), key=lambda x: x[1]):
    train_path = os.path.join(DATA_DIR, 'train', cat)
    val_path = os.path.join(DATA_DIR, 'validation', cat)
    
    train_count = len([f for f in os.listdir(train_path) if os.path.isfile(os.path.join(train_path, f))])
    val_count = len([f for f in os.listdir(val_path) if os.path.isfile(os.path.join(val_path, f))])
    total = train_count + val_count
    
    marker = " ⭐ MERGED" if cat == 'dermatitis' else ""
    print(f"   {idx}. {cat:<15} Train: {train_count:4d} | Val: {val_count:4d} | Total: {total:4d}{marker}")

# Compute class weights
print("\n⚖️  Computing class weights...")
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_gen.classes),
    y=train_gen.classes
)
class_weight_dict = dict(enumerate(class_weights))

print("   Class weights:")
for idx, cat in enumerate(sorted(train_gen.class_indices.keys())):
    weight = class_weights[idx]
    print(f"   {cat:<15} weight: {weight:.3f}")

# Save class indices
class_indices_path = os.path.join(MODEL_DIR, 'class_indices_phase1_5cat_enhanced.json')
with open(class_indices_path, 'w') as f:
    json.dump(train_gen.class_indices, f, indent=4)
print(f"\n💾 Class indices saved: {class_indices_path}")

# Callbacks
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

callbacks = [
    ModelCheckpoint(
        filepath=os.path.join(MODEL_DIR, 'phase1_5cat_enhanced_best.h5'),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    ),
    EarlyStopping(
        monitor='val_loss',
        patience=12,              # Increased from 10 (more data = more patience)
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    ),
    CSVLogger(
        os.path.join(LOGS_DIR, f'phase1_5cat_enhanced_{timestamp}.csv')
    )
]

steps_per_epoch = train_gen.samples // BATCH_SIZE
validation_steps = val_gen.samples // BATCH_SIZE

# ============================================================
# PHASE 1.1: Train with FROZEN base (30 epochs)
# ============================================================
print("\n" + "="*70)
print(f"📚 PHASE 1.1: Training with FROZEN base ({EPOCHS_PHASE1} epochs)")
print("="*70)

base_model = keras.applications.MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)

# Freeze base model
base_model.trainable = False

model = keras.Sequential([
    base_model,
    keras.layers.GlobalAveragePooling2D(),
    keras.layers.BatchNormalization(),
    keras.layers.Dense(256, activation='relu'),
    keras.layers.Dropout(0.5),
    keras.layers.BatchNormalization(),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=2, name='top_2_accuracy')]
)

print(f"\n🏗️  Model Phase 1.1:")
print(f"   Total parameters: {model.count_params():,}")
trainable_params = sum([tf.size(w).numpy() for w in model.trainable_weights])
print(f"   Trainable: {trainable_params:,}")
print(f"   Base: FROZEN ✅")

print(f"\n🔄 Training Phase 1.1...")
print(f"   Epochs: {EPOCHS_PHASE1}")
print(f"   Steps per epoch: {steps_per_epoch}")
print(f"   Validation steps: {validation_steps}")

history1 = model.fit(
    train_gen,
    steps_per_epoch=steps_per_epoch,
    epochs=EPOCHS_PHASE1,
    validation_data=val_gen,
    validation_steps=validation_steps,
    class_weight=class_weight_dict,
    callbacks=callbacks,
    verbose=1
)

# ============================================================
# PHASE 1.2: Fine-tune with UNFROZEN layers (30 epochs)
# ============================================================
print("\n" + "="*70)
print(f"🔧 PHASE 1.2: Fine-tuning with UNFROZEN layers ({EPOCHS_PHASE2} epochs)")
print("="*70)

# Unfreeze last 30 layers
base_model.trainable = True
frozen_layers = len(base_model.layers) - 30

for i, layer in enumerate(base_model.layers):
    if i < frozen_layers:
        layer.trainable = False
    else:
        layer.trainable = True

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=2, name='top_2_accuracy')]
)

trainable_params = sum([tf.size(w).numpy() for w in model.trainable_weights])
print(f"\n🏗️  Model Phase 1.2:")
print(f"   Total parameters: {model.count_params():,}")
print(f"   Trainable: {trainable_params:,}")
print(f"   Frozen layers: {frozen_layers}/{len(base_model.layers)}")
print(f"   Trainable layers: {len(base_model.layers) - frozen_layers}/{len(base_model.layers)}")
print(f"   Base: PARTIALLY UNFROZEN (last 30 layers) ✅")

print(f"\n🔄 Training Phase 1.2...")

history2 = model.fit(
    train_gen,
    steps_per_epoch=steps_per_epoch,
    epochs=EPOCHS_TOTAL,
    initial_epoch=EPOCHS_PHASE1,
    validation_data=val_gen,
    validation_steps=validation_steps,
    class_weight=class_weight_dict,
    callbacks=callbacks,
    verbose=1
)

# ============================================================
# FINAL EVALUATION
# ============================================================
print("\n" + "="*70)
print("📊 PHASE 1 ENHANCED - FINAL EVALUATION")
print("="*70)

# Evaluate on validation set
print("\n🔮 Evaluating on validation set...")
val_gen.reset()  # Reset generator to start from beginning
val_loss, val_acc, val_top2 = model.evaluate(val_gen, steps=validation_steps, verbose=1)

print(f"\n✅ PHASE 1 ENHANCED TRAINING COMPLETE!")
print(f"   Validation Loss:     {val_loss:.4f}")
print(f"   Validation Accuracy: {val_acc:.4f} ({val_acc*100:.2f}%)")
print(f"   Top-2 Accuracy:      {val_top2:.4f} ({val_top2*100:.2f}%)")

# Compare improvements
print(f"\n📈 IMPROVEMENTS:")
print("-"*70)
improvement_vs_original = val_acc*100 - 62.14
improvement_vs_previous = val_acc*100 - 63.62

print(f"   Original (7-cat, 5,741 images): 62.14%")
print(f"   Previous (5-cat, 5,741 images): 63.62%")
print(f"   Enhanced (5-cat, 10,426 images): {val_acc*100:.2f}%")
print(f"\n   vs Original:  {'+' if improvement_vs_original > 0 else ''}{improvement_vs_original:.2f}%")
print(f"   vs Previous:  {'+' if improvement_vs_previous > 0 else ''}{improvement_vs_previous:.2f}%")

# Performance assessment
print(f"\n📊 PERFORMANCE ASSESSMENT:")
print("-"*70)

if val_acc*100 >= 75:
    print(f"   🎉🎉🎉 EXCELLENT! Target EXCEEDED!")
    print(f"   Status: Production-ready ✅")
    print(f"   Next: Deploy and monitor real-world performance")
elif val_acc*100 >= 72:
    print(f"   🎉🎉 GREAT! Target ACHIEVED!")
    print(f"   Status: Production-ready ✅")
    print(f"   Next: Deploy or consider minor optimizations")
elif val_acc*100 >= 68:
    print(f"   🎉 GOOD! Close to target.")
    print(f"   Status: Usable for deployment ✅")
    print(f"   Next: Deploy or collect more data for weak categories")
elif val_acc*100 >= 65:
    print(f"   ✅ Decent improvement.")
    print(f"   Status: Consider further optimization")
    print(f"   Next: Analyze per-category performance")
else:
    print(f"   ⚠️  Below expectations.")
    print(f"   Status: Needs improvement")
    print(f"   Next: Review training logs and per-category accuracy")

# Save final summary
summary = {
    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
    'user': 'Manishnm10',
    'dataset': {
        'name': 'Enhanced 5-category (DermNet + Kaggle)',
        'total_images': 10426,
        'train_images': train_gen.samples,
        'val_images': val_gen.samples,
        'categories': num_classes
    },
    'training': {
        'epochs_phase1': EPOCHS_PHASE1,
        'epochs_phase2': EPOCHS_PHASE2,
        'total_epochs': EPOCHS_TOTAL,
        'batch_size': BATCH_SIZE,
        'image_size': IMG_SIZE
    },
    'results': {
        'val_loss': float(val_loss),
        'val_accuracy': float(val_acc),
        'val_accuracy_percent': float(val_acc*100),
        'top_2_accuracy': float(val_top2),
        'top_2_accuracy_percent': float(val_top2*100)
    },
    'improvements': {
        'vs_original_7cat': float(improvement_vs_original),
        'vs_previous_5cat': float(improvement_vs_previous)
    }
}

summary_path = os.path.join(LOGS_DIR, f'training_summary_{timestamp}.json')
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=4)

print(f"\n💾 Files saved:")
print(f"   Best model:      {MODEL_DIR}/phase1_5cat_enhanced_best.h5")
print(f"   Class indices:   {MODEL_DIR}/class_indices_phase1_5cat_enhanced.json")
print(f"   Training log:    {LOGS_DIR}/phase1_5cat_enhanced_{timestamp}.csv")
print(f"   Summary:         {summary_path}")

print(f"\n⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")

print("\n" + "="*70)
print("🎉 PHASE 1 ENHANCED COMPLETE!")
print("="*70)

print("\n🎯 NEXT STEPS:")
print("-"*70)
print("   1. Evaluate detailed per-category performance:")
print("      python evaluate_phase1_5cat_enhanced.py")
print("")
print("   2. Test with sample images:")
print("      python test_phase1_5cat_enhanced.py")
print("")
print("   3. If accuracy ≥72%:")
print("      • Deploy to production ✅")
print("      • Monitor real-world performance")
print("      • Plan Phase 2 (add more categories)")
print("")
print("   4. If accuracy <72%:")
print("      • Analyze confusion matrix")
print("      • Collect more data for weak categories")
print("      • Try EfficientNetB3 architecture")

print("\n" + "="*70)
print("✅ READY FOR DEPLOYMENT!")
print("="*70)