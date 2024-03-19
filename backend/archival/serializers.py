from rest_framework import serializers
from .models import *

class MarsMainTableDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarsMainTableData
        fields = '__all__'
        
        
class MarsBandInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarsBandInformation
        fields = '__all__'

        
class MarsBoundsCoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarsBoundsCoordinates
        fields = '__all__'
        
