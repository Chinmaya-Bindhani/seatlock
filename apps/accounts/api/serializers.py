from apps.accounts.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import  serializers
from django.contrib.auth.password_validation import  validate_password


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,trim_whitespace=False,)
    confirm_password = serializers.CharField(write_only=True,trim_whitespace=False,)

    class Meta:
        model = User
        fields = ['email','username','first_name','last_name','password','confirm_password',]

    def validate_email(self,value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("email is already associated with out platform ")
        return  value

    def validate(self,data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("password and confirm_password does not match")
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            username = validated_data['username'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
            password = validated_data['password']
        )
        return user

class LoginSerializers(serializers.Serializer):
    email=serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True,trim_whitespace=False)


