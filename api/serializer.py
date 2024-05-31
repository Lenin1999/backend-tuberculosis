from rest_framework import serializers
from.models import User
from.models import Registro

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('__all__')

class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registro
        fields = ('__all__')