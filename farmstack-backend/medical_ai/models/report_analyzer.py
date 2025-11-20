"""
Medical Report Analyzer
Analyzes medical reports and provides simplified explanations
"""

import cv2
import pytesseract
import numpy as np
from PIL import Image
import re
import os
import logging

logger = logging.getLogger('medical_ai')


class MedicalReportAnalyzer:
    """Analyze medical reports and provide simplified explanations"""
    
    def __init__(self):
        # Set tesseract path for Windows
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Medical terms dictionary with simple explanations
        self.medical_terms = {
            # Common CT/MRI terms
            "lesion": "an area of abnormal tissue",
            "nodule": "a small lump or growth",
            "mass": "a lump or growth in the body",
            "edema": "swelling caused by fluid buildup",
            "inflammation": "redness and swelling due to body's response",
            "hemorrhage": "bleeding inside the body",
            "fracture": "a broken bone",
            "stenosis": "narrowing of a passage or vessel",
            "hypertrophy": "enlargement of an organ or tissue",
            "atrophy": "shrinking or wasting away of tissue",
            
            # Lab report terms
            "elevated": "higher than normal",
            "decreased": "lower than normal",
            "hemoglobin": "protein that carries oxygen in blood",
            "glucose": "blood sugar level",
            "cholesterol": "fat-like substance in blood",
            "creatinine": "waste product that shows kidney function",
            "bilirubin": "yellow substance from broken down red blood cells",
            "wbc": "white blood cells - fight infections",
            "rbc": "red blood cells - carry oxygen",
            "platelet": "cells that help blood clot",
            
            # General terms
            "benign": "not cancerous, not harmful",
            "malignant": "cancerous, harmful",
            "chronic": "long-lasting condition",
            "acute": "sudden and severe",
            "prognosis": "expected outcome of a disease"
        }
        
        self.remedies = {
            "elevated glucose": [
                "Exercise regularly (30 minutes daily)",
                "Reduce sugar and refined carbs intake",
                "Drink plenty of water",
                "Include fiber-rich foods in diet",
                "Get adequate sleep (7-8 hours)"
            ],
            "elevated cholesterol": [
                "Eat more omega-3 rich foods (fish, nuts)",
                "Increase soluble fiber intake (oats, beans)",
                "Exercise regularly",
                "Avoid trans fats and processed foods",
                "Maintain healthy weight"
            ],
            "low hemoglobin": [
                "Eat iron-rich foods (spinach, red meat, lentils)",
                "Include vitamin C to improve iron absorption",
                "Eat folate-rich foods (leafy greens, citrus)",
                "Consider vitamin B12 supplements",
                "Avoid tea/coffee with meals"
            ],
            "inflammation": [
                "Apply ice to reduce swelling",
                "Rest the affected area",
                "Take turmeric (natural anti-inflammatory)",
                "Eat omega-3 rich foods",
                "Stay hydrated"
            ]
        }
    
    def preprocess_image(self, image_path):
        """Preprocess image for better OCR results"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Could not read image: {image_path}")
                return None
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Denoise
            denoised = cv2.medianBlur(thresh, 3)
            
            return denoised
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return None
    
    def extract_text(self, image_path):
        """Extract text from medical report image"""
        try:
            processed_img = self.preprocess_image(image_path)
            if processed_img is None:
                return ""
                
            text = pytesseract.image_to_string(processed_img)
            logger.info(f"Extracted {len(text)} characters from image")
            return text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def analyze_report(self, image_path):
        """Analyze medical report and provide summary"""
        logger.info(f"Analyzing report: {image_path}")
        
        # Extract text
        text = self.extract_text(image_path)
        
        if not text:
            return {
                "success": False,
                "message": "Unable to extract text from image. Please ensure the image is clear and readable."
            }
        
        # Convert to lowercase for analysis
        text_lower = text.lower()
        
        # Find medical terms
        found_terms = {}
        for term, explanation in self.medical_terms.items():
            if term in text_lower:
                found_terms[term] = explanation
        
        # Extract numerical values (for lab reports)
        numbers = re.findall(r'(\w+)\s*[:-]?\s*(\d+\.?\d*)\s*(mg|mmol|g|dl)?', text_lower)
        
        # Identify issues
        issues = []
        recommendations = []
        
        for term in found_terms.keys():
            if term in ["elevated", "high", "increased"]:
                issues.append("Some values are higher than normal")
            elif term in ["decreased", "low", "reduced"]:
                issues.append("Some values are lower than normal")
        
        # Get recommendations based on findings
        for condition, remedies in self.remedies.items():
            if condition in text_lower:
                recommendations.extend(remedies)
        
        # Generate summary
        summary = {
            "success": True,
            "extracted_text": text[:500] + "..." if len(text) > 500 else text,  # Limit text length
            "medical_terms_found": found_terms,
            "key_findings": list(set(issues)) if issues else ["No specific issues detected in automated analysis"],
            "recommendations": list(set(recommendations))[:8] if recommendations else [
                "Consult with your healthcare provider for detailed interpretation",
                "Maintain a healthy lifestyle with balanced diet and regular exercise",
                "Keep track of your symptoms and report changes to your doctor"
            ],
            "disclaimer": "⚠️ This is an automated analysis and should not replace professional medical advice. Please consult your doctor for accurate diagnosis and treatment."
        }
        
        logger.info(f"Analysis complete. Found {len(found_terms)} medical terms")
        return summary
    
    def simplify_text(self, medical_text):
        """Simplify medical terminology in text"""
        simplified = medical_text
        for term, explanation in self.medical_terms.items():
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            simplified = pattern.sub(f"{term} ({explanation})", simplified)
        
        return simplified