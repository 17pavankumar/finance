from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('role',)

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'is_active')

class UserManagementSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, write_only=True, required=False)
    role_display = serializers.CharField(source='profile.role', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'is_active', 'role', 'role_display')
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    def create(self, validated_data):
        role = validated_data.pop('role', 'viewer')
        user = User.objects.create_user(**validated_data)
        user.profile.role = role
        user.profile.save()
        return user

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if role:
            instance.profile.role = role
            instance.profile.save()
        return instance

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        # By default gets 'viewer' via signal
        user = User.objects.create_user(**validated_data)
        return user
