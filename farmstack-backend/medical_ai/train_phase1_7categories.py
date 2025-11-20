"""
PHASE 1 TRAINING - FIXED VERSION
Proper transfer learning with correct layer freezing
Date: 2025-11-05 10:36:00 UTC
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
EPOCHS = 100  # Increased for 2-phase training
DATA_DIR = 'data/skin_diseases_phase1_7cat'
MODEL_DIR = 'models'
LOGS_DIR = 'logs'

print("\n" + "="*70)
print("🚀 PHASE 1: TRAINING 7 CORE SKIN CONDITIONS (FIXED)")
print("="*70)
print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
print(f"👤 User: Manishnm10")

# Create directories
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Prepare data
print("\n📊 Preparing data generators...")

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.15,
    zoom_range=0.15,
    horizontal_flip=True,
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
print(f"✅ Classes: {list(train_gen.class_indices.keys())}")

# Compute class weights
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_gen.classes),
    y=train_gen.classes
)
class_weight_dict = dict(enumerate(class_weights))

# Save class indices
with open(os.path.join(MODEL_DIR, 'class_indices_phase1.json'), 'w') as f:
    json.dump(train_gen.class_indices, f, indent=4)

# Callbacks
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

callbacks = [
    ModelCheckpoint(
        filepath=os.path.join(MODEL_DIR, 'phase1_best.h5'),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    ),
    EarlyStopping(
        monitor='val_loss',
        patience=15,
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
        os.path.join(LOGS_DIR, f'phase1_{timestamp}.csv')
    )
]

steps_per_epoch = train_gen.samples // BATCH_SIZE
validation_steps = val_gen.samples // BATCH_SIZE

# ============================================================
# PHASE 1: Train with frozen base (30 epochs)
# ============================================================
print("\n" + "="*70)
print("📚 PHASE 1.1: Training with FROZEN base model (30 epochs)")
print("="*70)

# Create base model
base_model = keras.applications.MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)

# FREEZE ALL base layers
base_model.trainable = False

# Build model
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

# Compile
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=2, name='top_2_accuracy')]
)

print(f"\n🏗️  Model Phase 1.1:")
print(f"   Total parameters: {model.count_params():,}")
trainable_params = sum([tf.size(w).numpy() for w in model.trainable_weights])
print(f"   Trainable parameters: {trainable_params:,}")
print(f"   Base model: FROZEN ✅")

# Train Phase 1.1
history1 = model.fit(
    train_gen,
    steps_per_epoch=steps_per_epoch,
    epochs=30,
    validation_data=val_gen,
    validation_steps=validation_steps,
    class_weight=class_weight_dict,
    callbacks=callbacks,
    verbose=1
)

# ============================================================
# PHASE 1.2: Fine-tune with unfrozen layers (70 epochs)
# ============================================================
print("\n" + "="*70)
print("🔧 PHASE 1.2: Fine-tuning with UNFROZEN layers (70 epochs)")
print("="*70)

# Unfreeze last 30 layers of base model
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

# Recompile with lower learning rate
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.0001),  # Lower LR
    loss='categorical_crossentropy',
    metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=2, name='top_2_accuracy')]
)

trainable_params = sum([tf.size(w).numpy() for w in model.trainable_weights])
print(f"\n🏗️  Model Phase 1.2:")
print(f"   Total parameters: {model.count_params():,}")
print(f"   Trainable parameters: {trainable_params:,}")
print(f"   Base model: PARTIALLY UNFROZEN (last 30 layers) ✅")

# Train Phase 1.2
history2 = model.fit(
    train_gen,
    steps_per_epoch=steps_per_epoch,
    epochs=70,
    initial_epoch=30,
    validation_data=val_gen,
    validation_steps=validation_steps,
    class_weight=class_weight_dict,
    callbacks=callbacks,
    verbose=1
)

# Final evaluation
print("\n" + "="*70)
print("📊 PHASE 1 FINAL EVALUATION")
print("="*70)

val_loss, val_acc, val_top2 = model.evaluate(val_gen, steps=validation_steps)

print(f"\n✅ PHASE 1 TRAINING COMPLETE!")
print(f"   Validation Loss: {val_loss:.4f}")
print(f"   Validation Accuracy: {val_acc:.4f} ({val_acc*100:.2f}%)")
print(f"   Top-2 Accuracy: {val_top2:.4f} ({val_top2*100:.2f}%)")

improvement = val_acc*100 - 63.39
print(f"\n📈 IMPROVEMENT:")
print(f"   Previous: 63.39%")
print(f"   Phase 1:  {val_acc*100:.2f}%")
print(f"   Gain:     {'+' if improvement > 0 else ''}{improvement:.2f}%")

print(f"\n💾 Model saved: {MODEL_DIR}/phase1_best.h5")
print(f"⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")

print("\n🎉 READY FOR DEPLOYMENT!")