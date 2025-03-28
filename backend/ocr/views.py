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
import logging

# Create your views here.

logger = logging.getLogger('ocr')

class HandwrittenTextViewSet(viewsets.ModelViewSet):
    queryset = HandwrittenText.objects.all()
    serializer_class = HandwrittenTextSerializer

    def preprocess_image(self, image):
        try:
            logger.debug(f"Starting enhanced image preprocessing, shape: {image.shape}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Increase contrast more aggressively
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4,4))  # Adjusted parameters
            enhanced = clahe.apply(gray)
            
            # Reduce noise while preserving edges
            denoised = cv2.fastNlMeansDenoising(enhanced, h=20)  # Increased denoising strength
            
            # More aggressive thresholding for clear text
            thresh = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                15,  # Smaller block size for clearer letters
                5    # Reduced C constant
            )
            
            # Connect broken parts of letters
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
            dilated = cv2.dilate(thresh, kernel, iterations=1)
            
            # Clean up small noise
            kernel = np.ones((2,2), np.uint8)
            cleaned = cv2.morphologyEx(dilated, cv2.MORPH_OPEN, kernel)
            
            # Invert back for OCR
            final = cv2.bitwise_not(cleaned)
            
            return final

        except Exception as e:
            logger.error(f"Error in preprocessing: {str(e)}", exc_info=True)
            raise

    @action(detail=True, methods=['post'])
    def process_image(self, request, pk=None):
        instance = self.get_object()
        try:
            logger.info(f"Starting image processing for ID: {pk}")
            instance.status = 'processing'
            instance.save()

            # Read image with higher resolution
            image_path = instance.image.path
            img = cv2.imread(image_path, cv2.IMREAD_COLOR)
            
            if img is None:
                raise Exception("Failed to read image file")
            
            # Resize if image is too small
            min_height = 800
            if img.shape[0] < min_height:
                scale = min_height / img.shape[0]
                img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
                logger.info(f"Resized image to height {img.shape[0]}")

            processed_img = self.preprocess_image(img)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(processed_img)
            
            # Configure Tesseract for handwriting
            custom_config = r'--oem 3 --psm 6 -l eng --dpi 300'
            extracted_text = pytesseract.image_to_string(
                pil_image,
                config=custom_config
            )
            
            if not extracted_text.strip():
                logger.warning("No text extracted, trying different PSM mode")
                # Try different page segmentation mode
                custom_config = r'--oem 3 --psm 3 -l eng --dpi 300'
                extracted_text = pytesseract.image_to_string(
                    pil_image,
                    config=custom_config
                )

            instance.extracted_text = extracted_text
            instance.status = 'completed'
            instance.save()

            return Response({
                'status': 'success',
                'extracted_text': extracted_text
            })

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}", exc_info=True)
            instance.status = 'failed'
            instance.save()
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
