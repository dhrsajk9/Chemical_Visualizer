from rest_framework import serializers
from .models import EquipmentData

class EquipmentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentData
        fields = ['id', 'file', 'uploaded_at', 'filename']