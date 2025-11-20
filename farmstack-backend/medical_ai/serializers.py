"""
Serializers for Medical AI API endpoints
"""

from rest_framework import serializers
from django.conf import settings


class SkinDiseaseUploadSerializer(serializers.Serializer):
    """Serializer for skin disease image upload"""
    image = serializers.ImageField()
    
    def validate_image(self, value):
        # Validate file size
        max_size = settings.MEDICAL_AI_SETTINGS['MAX_UPLOAD_SIZE']
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Image file size should not exceed {max_size // (1024*1024)}MB"
            )
        
        # Validate file type
        valid_extensions = settings.MEDICAL_AI_SETTINGS['ALLOWED_IMAGE_FORMATS']
        ext = value.name.split('.')[-1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f"Only {', '.join(valid_extensions).upper()} files are allowed"
            )
        
        return value


class MedicalReportUploadSerializer(serializers.Serializer):
    """Serializer for medical report upload"""
    report = serializers.FileField()
    report_type = serializers.ChoiceField(
        choices=['ct_scan', 'mri', 'lab_report', 'xray', 'other'],
        default='other',
        required=False
    )
    
    def validate_report(self, value):
        # Validate file size
        max_size = settings.MEDICAL_AI_SETTINGS['MAX_UPLOAD_SIZE']
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size should not exceed {max_size // (1024*1024)}MB"
            )
        
        # Validate file type
        valid_extensions = settings.MEDICAL_AI_SETTINGS['ALLOWED_REPORT_FORMATS']
        ext = value.name.split('.')[-1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f"Only {', '.join(valid_extensions).upper()} files are allowed"
            )
        
        return value