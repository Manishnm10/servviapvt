"""
API Views for Medical AI module
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
import logging

from .serializers import SkinDiseaseUploadSerializer, MedicalReportUploadSerializer
from .utils import SkinDiseaseDetector
from .models.report_analyzer import MedicalReportAnalyzer

logger = logging.getLogger('medical_ai')


class HealthCheckView(APIView):
    """Health check endpoint for Medical AI module"""
    permission_classes = []  # Allow unauthenticated access
    
    def get(self, request):
        """Get health status"""
        # Check if model file exists
        model_path = settings.MEDICAL_AI_SETTINGS['MODEL_PATH']
        model_exists = os.path.exists(model_path)
        
        return Response({
            'status': 'healthy',
            'service': 'Medical AI Module',
            'version': '1.0.0',
            'features': [
                'Skin Disease Detection (acne, psoriasis, ringworm, rash)',
                'Medical Report Analysis'
            ],
            'model_loaded': model_exists,
            'model_path': model_path if model_exists else 'Model not found'
        })


class SkinDiseaseDetectionView(APIView):
    """API endpoint for skin disease detection"""
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Upload and analyze skin disease image"""
        logger.info(f"Skin disease detection request from user: {request.user}")
        
        serializer = SkinDiseaseUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(f"Invalid request data: {serializer.errors}")
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Save uploaded image
            image = serializer.validated_data['image']
            file_name = f'skin_disease_{request.user.id}_{image.name}'
            file_path = os.path.join(settings.MEDICAL_AI_UPLOADS, file_name)
            
            # Ensure directory exists
            os.makedirs(settings.MEDICAL_AI_UPLOADS, exist_ok=True)
            
            # Save file
            with open(file_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            
            logger.info(f"Image saved to: {file_path}")
            
            # Detect disease
            detector = SkinDiseaseDetector()
            result = detector.predict(file_path)
            
            # Clean up uploaded file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not delete temporary file: {e}")
            
            if result['success']:
                logger.info(f"Detection successful: {result['disease']}")
                return Response(result, status=status.HTTP_200_OK)
            else:
                logger.error(f"Detection failed: {result.get('error')}")
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Unexpected error in skin disease detection: {e}")
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MedicalReportAnalysisView(APIView):
    """API endpoint for medical report analysis"""
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Upload and analyze medical report"""
        logger.info(f"Medical report analysis request from user: {request.user}")
        
        serializer = MedicalReportUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(f"Invalid request data: {serializer.errors}")
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Save uploaded report
            report = serializer.validated_data['report']
            report_type = serializer.validated_data.get('report_type', 'other')
            file_name = f'report_{request.user.id}_{report.name}'
            file_path = os.path.join(settings.MEDICAL_AI_UPLOADS, file_name)
            
            # Ensure directory exists
            os.makedirs(settings.MEDICAL_AI_UPLOADS, exist_ok=True)
            
            # Save file
            with open(file_path, 'wb+') as destination:
                for chunk in report.chunks():
                    destination.write(chunk)
            
            logger.info(f"Report saved to: {file_path}")
            
            # Analyze report
            analyzer = MedicalReportAnalyzer()
            result = analyzer.analyze_report(file_path)
            result['report_type'] = report_type
            
            # Clean up uploaded file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not delete temporary file: {e}")
            
            if result['success']:
                logger.info("Report analysis successful")
                return Response(result, status=status.HTTP_200_OK)
            else:
                logger.error(f"Report analysis failed: {result.get('message')}")
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Unexpected error in report analysis: {e}")
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )