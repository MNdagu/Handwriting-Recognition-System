from rest_framework import serializers
from .models import HandwrittenText

class HandwrittenTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = HandwrittenText
        fields = ['id', 'image', 'extracted_text', 'created_at', 'updated_at', 'status']
        read_only_fields = ['extracted_text', 'created_at', 'updated_at', 'status'] 