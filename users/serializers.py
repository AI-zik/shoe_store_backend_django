from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.db.models import Q, Max, Min, Avg
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from shoes.validators import validate_password as password_validate
from .models import User


class UserListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'other_name', 'email', 'image_url']

    def get_image_url(self, object):
        return object.image.url


class UserDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = User
        exclude = ['password', ]

    def get_image_url(self, object):
        return object.image.url

class RegisterUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[password_validate])
    
    class Meta:
        model = User
        fields = "__all__"

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise ValidationError({"password" : "Password fields don't match"})
        return data
    

    def create(self, validated_data):
        user = User()
        for field in validated_data:
            print(field)
            if field == "first_name":
                user.first_name = validated_data['first_name']
            if field == "last_name":
                user.last_name = validated_data['last_name']
            if field == "other_name":
                user.other_name = validated_data['other_name']
            if field == "email":
                user.email = validated_data['email']
            if field == "phone_number":
                user.phone_number = validated_data['phone_number']
            if field == "image" :
                user.image = validated_data['image']
            if field == "zip_code":
                user.zip_code = validated_data['zip_code']
            if field == "city":
                user.city = validated_data['city']
            if field == "country":
                user.country = validated_data['country']
            if field == "user_type":
                user.user_type = validated_data['user_type']

        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        fields = ['email', 'password']

    def validate(self, data):
        user = authenticate(email = data['email'], password= data['password'])
        if not user:
            raise ValidationError(_("Invalid login cridentials"))
        return data


class UpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ["password"]

    def validate_user_type(self, value):
        user = self.instance
        request = self.context['request']
        if not request.user.user_type == 1:
            raise ValidationError(_("Only admins can change the user type of a user"))
        return value

class PasswordChangeSerializer(serializers.ModelSerializer):

    new_password = serializers.CharField(required=True, write_only=True, validators=[password_validate])
    old_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ["old_password", "new_password", "confirm_password"]


    def validate_old_password(self, value):
        user = self.instance
        if not user.check_password(value):
            raise ValidationError(_("Incorrect password"))
        return value

    def validate(self, data):
        if not data['confirm_password'] == data['new_password']:
            raise ValidationError({"confirm_password" : "Password fields don't match"})
        return data

    def update(self, instance, validated_data):
        user = self.context['request'].user

        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance