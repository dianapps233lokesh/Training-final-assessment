from rest_framework import serializers

from authentication.models import UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "phone",
            "address",
            "city",
            "state",
            "pincode",
            "user_type",
        )
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "phone": {"required": False},
            "address": {"required": False},
            "city": {"required": False},
            "state": {"required": False},
            "pincode": {"required": False},
        }

    def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "address",
            "city",
            "state",
            "pincode",
            "user_type",
        )
        read_only_fields = ("user_type", "username")
