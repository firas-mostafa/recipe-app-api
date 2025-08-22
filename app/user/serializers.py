# Serializers for the user API view
from django.contrib.auth import (
    get_user_model,
    authenticate
    )
# from django.utils.translation import gettext as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    # Serializer for the user object

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name', 'image']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        # Create & return user with encrypted password
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        # Update & return user with encrypted password
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    # Serializer for user auth token
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        # Validate and authenticate the user

        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = ('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['email', 'image']
        read_only_fields = ['email']
        extra_kwargs = {'image': {'required': 'True'}}
