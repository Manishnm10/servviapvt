"""
URL Configuration for Medical AI module
"""

from django.urls import path
from .views import (
    HealthCheckView,
    SkinDiseaseDetectionView,
    MedicalReportAnalysisView
)

app_name = 'medical_ai'

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('skin-disease/detect/', SkinDiseaseDetectionView.as_view(), name='skin-disease-detect'),
    path('medical-report/analyze/', MedicalReportAnalysisView.as_view(), name='medical-report-analyze'),
]