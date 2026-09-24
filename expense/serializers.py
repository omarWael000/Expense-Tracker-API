from rest_framework import serializers

from .models import Expense,Category

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model= Expense
        fields= (
            'amount','description','category'
        )

    

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'email',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        user = authenticate(username= data['username'], password= data['password'])

        if user is None:
            raise serializers.ValidationError("Invalid username or password.")

        data['user']= user

        return data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model= Category
        fields= ('id','name')
