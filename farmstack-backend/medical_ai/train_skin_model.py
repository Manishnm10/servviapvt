"""
Enhanced training script for skin disease detection
Optimized for DermNet dataset with 5741 images
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, 
    TensorBoard, CSVLogger
)
import numpy as np
import os
import json
from datetime import datetime

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 100
DATA_DIR = 'data/skin_diseases_organized'  # Updated path
MODEL_DIR = 'models'
LOGS_DIR = 'logs'

class SkinDiseaseTrainer:
    def __init__(self):
        self.img_size = IMG_SIZE
        self.batch_size = BATCH_SIZE
        self.epochs = EPOCHS
        self.data_dir = DATA_DIR
        self.model_dir = MODEL_DIR
        self.classes = ['acne', 'psoriasis', 'ringworm', 'rash']
        
        # Create directories
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)
        
    def create_model(self):
        """Create an improved CNN model using MobileNetV2"""
        print("\n🏗️  Creating model architecture...")
        
        # Load pre-trained MobileNetV2
        base_model = keras.applications.MobileNetV2(
            input_shape=(self.img_size, self.img_size, 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model initially
        base_model.trainable = False
        
        # Build model
        model = keras.Sequential([
            # Input layer
            layers.Input(shape=(self.img_size, self.img_size, 3)),
            
            # Base model
            base_model,
            
            # Custom top layers
            layers.GlobalAveragePooling2D(),
            layers.BatchNormalization(),
            
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.BatchNormalization(),
            
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            
            # Output layer
            layers.Dense(len(self.classes), activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=2, name='top_2_accuracy')]
        )
        
        print("✅ Model created successfully!")
        model.summary()
        
        return model, base_model
    
    def prepare_data(self):
        """Prepare training and validation data with augmentation"""
        print("\n📊 Preparing data generators...")
        
        # Training data augmentation
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=30,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            vertical_flip=False,
            fill_mode='nearest',
            brightness_range=[0.8, 1.2]
        )
        
        # Validation data - only rescaling
        val_datagen = ImageDataGenerator(rescale=1./255)
        
        # Load training data
        train_generator = train_datagen.flow_from_directory(
            os.path.join(self.data_dir, 'train'),
            target_size=(self.img_size, self.img_size),
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=True,
            seed=42
        )
        
        # Load validation data
        validation_generator = val_datagen.flow_from_directory(
            os.path.join(self.data_dir, 'validation'),
            target_size=(self.img_size, self.img_size),
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False,
            seed=42
        )
        
        print(f"✅ Training samples: {train_generator.samples}")
        print(f"✅ Validation samples: {validation_generator.samples}")
        print(f"✅ Classes: {train_generator.class_indices}")
        
        # Save class indices
        with open(os.path.join(self.model_dir, 'class_indices.json'), 'w') as f:
            json.dump(train_generator.class_indices, f, indent=4)
        
        return train_generator, validation_generator
    
    def get_callbacks(self):
        """Setup training callbacks"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        callbacks = [
            # Save best model
            ModelCheckpoint(
                filepath=os.path.join(self.model_dir, 'skin_disease_model_best.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                mode='max',
                verbose=1
            ),
            
            # Early stopping
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            
            # Reduce learning rate
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            
            # TensorBoard logging
            TensorBoard(
                log_dir=os.path.join(LOGS_DIR, f'training_{timestamp}'),
                histogram_freq=1
            ),
            
            # CSV logging
            CSVLogger(
                os.path.join(LOGS_DIR, f'training_{timestamp}.csv')
            )
        ]
        
        return callbacks
    
    def train(self):
        """Main training function"""
        print("\n" + "="*70)
        print("🚀 STARTING SKIN DISEASE MODEL TRAINING")
        print("="*70)
        print(f"📊 Dataset: {self.data_dir}")
        print(f"🎯 Expected accuracy: 80-90% (with 5741 images)")
        
        # Create model
        model, base_model = self.create_model()
        
        # Prepare data
        train_gen, val_gen = self.prepare_data()
        
        # Get callbacks
        callbacks = self.get_callbacks()
        
        # Calculate steps
        steps_per_epoch = train_gen.samples // self.batch_size
        validation_steps = val_gen.samples // self.batch_size
        
        print("\n📈 Training configuration:")
        print(f"   Epochs: {self.epochs}")
        print(f"   Batch size: {self.batch_size}")
        print(f"   Steps per epoch: {steps_per_epoch}")
        print(f"   Validation steps: {validation_steps}")
        
        # Phase 1: Train with frozen base
        print("\n" + "="*70)
        print("📚 PHASE 1: Training with frozen base model (30 epochs)")
        print("="*70)
        
        history_phase1 = model.fit(
            train_gen,
            steps_per_epoch=steps_per_epoch,
            epochs=30,
            validation_data=val_gen,
            validation_steps=validation_steps,
            callbacks=callbacks,
            verbose=1
        )
        
        # Phase 2: Fine-tune with unfrozen layers
        print("\n" + "="*70)
        print("🔧 PHASE 2: Fine-tuning with unfrozen layers")
        print("="*70)
        
        # Unfreeze base model
        base_model.trainable = True
        
        # Recompile with lower learning rate
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.TopKCategoricalAccuracy(k=2, name='top_2_accuracy')]
        )
        
        history_phase2 = model.fit(
            train_gen,
            steps_per_epoch=steps_per_epoch,
            epochs=self.epochs,
            initial_epoch=30,
            validation_data=val_gen,
            validation_steps=validation_steps,
            callbacks=callbacks,
            verbose=1
        )
        
        # Save final model
        final_model_path = os.path.join(self.model_dir, 'skin_disease_model_final.h5')
        model.save(final_model_path)
        
        print("\n" + "="*70)
        print("✅ TRAINING COMPLETE!")
        print("="*70)
        print(f"📁 Best model saved to: {self.model_dir}/skin_disease_model_best.h5")
        print(f"📁 Final model saved to: {final_model_path}")
        print(f"📁 Training logs saved to: {LOGS_DIR}/")
        
        # Evaluate on validation set
        print("\n📊 Final Evaluation:")
        val_loss, val_acc, val_top2 = model.evaluate(val_gen, steps=validation_steps)
        print(f"   Validation Loss: {val_loss:.4f}")
        print(f"   Validation Accuracy: {val_acc:.4f} ({val_acc*100:.2f}%)")
        print(f"   Top-2 Accuracy: {val_top2:.4f} ({val_top2*100:.2f}%)")
        
        return model, history_phase1, history_phase2

def main():
    # Set random seeds for reproducibility
    np.random.seed(42)
    tf.random.set_seed(42)
    
    # Check if GPU is available
    print("\n🖥️  System Information:")
    print(f"   TensorFlow version: {tf.__version__}")
    print(f"   GPU available: {len(tf.config.list_physical_devices('GPU')) > 0}")
    if tf.config.list_physical_devices('GPU'):
        print(f"   GPU devices: {tf.config.list_physical_devices('GPU')}")
    else:
        print("   ⚠️  No GPU detected. Training will use CPU (slower).")
    
    # Create trainer and start training
    trainer = SkinDiseaseTrainer()
    model, hist1, hist2 = trainer.train()
    
    print("\n" + "="*70)
    print("🎉 ALL DONE! Your model is ready to use.")
    print("="*70)
    print("\n🚀 Next steps:")
    print("   1. Test the model: python test_model.py")
    print("   2. Start Django server: cd .. && python manage.py runserver")
    print("   3. Test API at: http://localhost:8000/api/medical-ai/health/")

if __name__ == "__main__":
    main()