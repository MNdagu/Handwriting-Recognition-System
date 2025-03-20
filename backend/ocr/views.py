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

    def preprocess_image(self, image):
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,  # Block size
            2    # C constant
        )
        
        # Denoise the image
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        # Optional: Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        return enhanced

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
            
            if img is None:
                raise Exception("Failed to read image")

            # Preprocess the image
            processed_img = self.preprocess_image(img)
            
            # Convert to PIL Image for pytesseract
            pil_image = Image.fromarray(processed_img)

            # Perform OCR with custom configuration
            custom_config = r'--oem 3 --psm 6'
            extracted_text = pytesseract.image_to_string(
                pil_image,
                config=custom_config
            )

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
