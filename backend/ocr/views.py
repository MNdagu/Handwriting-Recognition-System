from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import HandwrittenText
from .serializers import HandwrittenTextSerializer
import pytesseract
import cv2
import numpy as np
from PIL import Image
import os

# Create your views here.

class HandwrittenTextViewSet(viewsets.ModelViewSet):
    queryset = HandwrittenText.objects.all()
    serializer_class = HandwrittenTextSerializer

    @action(detail=True, methods=['post'])
    def process_image(self, request, pk=None):
        instance = self.get_object()
        try:
            # Update status to processing
            instance.status = 'processing'
            instance.save()

            # Read the image
            image_path = instance.image.path
            img = cv2.imread(image_path)

            # Preprocess the image
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            # Convert to PIL Image for pytesseract
            pil_image = Image.fromarray(thresh)

            # Perform OCR
            extracted_text = pytesseract.image_to_string(pil_image)

            # Update the instance with extracted text
            instance.extracted_text = extracted_text
            instance.status = 'completed'
            instance.save()

            return Response({
                'status': 'success',
                'extracted_text': extracted_text
            })

        except Exception as e:
            instance.status = 'failed'
            instance.save()
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
