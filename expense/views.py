from django.shortcuts import render,get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .serializers import ExpenseSerializer, UserSerializer,LoginSerializer
from .models import Expense



# Create your views here.

class ExpenseView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request,id=None):

        if id is None:
            qs= Expense.objects.filter(user=request.user)
            serializer = ExpenseSerializer(qs, many=True)

            return Response(serializer.data)

        expense = get_object_or_404(Expense,id=id,user=request.user)
        
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)


    def post(self, request):

        serializer = ExpenseSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


    def put(self,request,id):

        expense = get_object_or_404(Expense,id=id,user=request.user)
                

        serializer = ExpenseSerializer(expense,data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self,request,id):

        expense = get_object_or_404(Expense,id=id,user=request.user)
                
        serializer = ExpenseSerializer(expense,data=request.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self,request,id):

        expense = get_object_or_404(Expense,id=id,user=request.user)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


   

class UserRegistrationView(APIView):

    def post(self, request):

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):

    def post(self,request):

        serializer=LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key
            })

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )