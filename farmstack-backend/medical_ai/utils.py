"""
Utility functions for Medical AI module
Includes skin disease detection
"""

import cv2
import numpy as np
from tensorflow import keras
from PIL import Image
import os
import logging
from django.conf import settings

logger = logging.getLogger('medical_ai')


class SkinDiseaseDetector:
    """Detect and classify skin diseases from images"""
    
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = settings.MEDICAL_AI_SETTINGS['MODEL_PATH']
            
        self.model_path = model_path
        self.model = None
        self.img_size = settings.MEDICAL_AI_SETTINGS['IMG_SIZE']
        self.classes = ['acne', 'psoriasis', 'ringworm', 'rash']
        
        # Home remedies for each condition
        self.remedies = {
            'acne': [
                "🧼 Wash face twice daily with gentle cleanser",
                "🍯 Apply honey mask (natural antibacterial)",
                "🌿 Use tea tree oil diluted with carrier oil",
                "🥒 Apply cucumber slices to reduce inflammation",
                "💧 Stay hydrated - drink 8 glasses of water daily",
                "🥗 Eat foods rich in omega-3 and zinc",
                "😴 Get adequate sleep (7-8 hours)",
                "🚫 Avoid touching your face frequently"
            ],
            'psoriasis': [
                "🧴 Apply aloe vera gel to affected areas",
                "🛁 Take oatmeal baths for relief",
                "🥥 Use coconut oil as natural moisturizer",
                "☀️ Get moderate sun exposure (15-20 minutes)",
                "🧘 Practice stress-reduction techniques",
                "🍎 Eat anti-inflammatory foods (turmeric, fish)",
                "💧 Keep skin well-moisturized",
                "🚭 Avoid smoking and alcohol"
            ],
            'ringworm': [
                "🧄 Apply crushed garlic (natural antifungal)",
                "🍎 Use apple cider vinegar diluted with water",
                "🌿 Apply tea tree oil to affected area",
                "🧼 Keep area clean and dry",
                "👔 Wear loose, breathable clothing",
                "🧺 Wash clothes and bedding in hot water",
                "🚿 Dry yourself thoroughly after bathing",
                "🤝 Avoid sharing personal items"
            ],
            'rash': [
                "❄️ Apply cold compress to reduce itching",
                "🧴 Use calamine lotion for relief",
                "🛁 Take lukewarm oatmeal baths",
                "🥥 Apply coconut oil or aloe vera",
                "🧼 Use mild, fragrance-free soap",
                "👔 Wear loose, soft cotton clothing",
                "🌡️ Keep the area cool and dry",
                "🚫 Avoid scratching the affected area"
            ]
        }
        
        self.descriptions = {
            'acne': "Acne occurs when hair follicles become clogged with oil and dead skin cells. It's very common and usually appears on the face, forehead, chest, and back.",
            'psoriasis': "Psoriasis is a skin condition that causes red, itchy, scaly patches. It's a chronic condition that can be managed with proper care and treatment.",
            'ringworm': "Ringworm is a fungal infection that causes a ring-shaped rash. Despite its name, it's not caused by a worm. It's contagious but treatable.",
            'rash': "A rash is an area of irritated or swollen skin. It can be caused by allergies, infections, or skin conditions. Most rashes are harmless and go away on their own."
        }
        
        # Try to load model
        self._load_model()
    
    def _load_model(self):
        """Load the trained model"""
        try:
            if os.path.exists(self.model_path):
                self.model = keras.models.load_model(self.model_path)
                logger.info(f"Model loaded successfully from {self.model_path}")
            else:
                logger.warning(f"Model file not found at {self.model_path}")
                self.model = None
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def preprocess_image(self, image_path):
        """Preprocess image for model prediction"""
        try:
            img = Image.open(image_path).convert('RGB')
            img = img.resize((self.img_size, self.img_size))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            return img_array
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise
    
    def predict(self, image_path):
        """Predict skin disease from image"""
        try:
            # Check if model is loaded
            if self.model is None:
                return {
                    'success': False,
                    'error': 'Model not loaded',
                    'message': 'The AI model is not available. Please ensure the model has been trained and is located at the correct path.'
                }
            
            # Preprocess image
            logger.info(f"Processing image: {image_path}")
            img_array = self.preprocess_image(image_path)
            
            # Make prediction
            predictions = self.model.predict(img_array, verbose=0)
            predicted_class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class_idx])
            predicted_class = self.classes[predicted_class_idx]
            
            # Get all probabilities
            all_predictions = {
                self.classes[i]: float(predictions[0][i]) 
                for i in range(len(self.classes))
            }
            
            logger.info(f"Prediction: {predicted_class} ({confidence*100:.2f}%)")
            
            result = {
                'success': True,
                'disease': predicted_class,
                'confidence': confidence,
                'all_predictions': all_predictions,
                'description': self.descriptions[predicted_class],
                'home_remedies': self.remedies[predicted_class],
                'recommendation': self._get_recommendation(predicted_class, confidence),
                'disclaimer': '⚠️ This is an AI-based analysis and should not replace professional medical advice. Please consult a dermatologist for proper diagnosis and treatment.'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Error processing image. Please try again with a clear image.'
            }
    
    def _get_recommendation(self, disease, confidence):
        """Get recommendation based on disease and confidence"""
        if confidence < 0.6:
            return "⚠️ Low confidence in prediction. Please consult a dermatologist for accurate diagnosis."
        elif confidence < 0.8:
            return "⚠️ Moderate confidence. Try the home remedies, but consult a doctor if symptoms persist for more than a week."
        else:
            return "✅ High confidence in prediction. You can try the suggested home remedies. Consult a doctor if symptoms worsen or don't improve in 2 weeks."


def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = settings.MEDICAL_AI_SETTINGS['ALLOWED_IMAGE_FORMATS']
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions