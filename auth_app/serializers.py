from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import get_user_model

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()  # Replace with your custom user model if needed
        fields = ['id', 'email', 'username', 'is_active','is_staff']  # Include the fields you need
