from django.shortcuts import render,get_object_or_404

from django.db.models import Sum, Count,F,Avg
from django.db.models.functions import TruncMonth

from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination

from .serializers import ExpenseSerializer, UserSerializer,LoginSerializer,CategorySerializer
from .models import Expense,Category



# Create your views here.

class ExpenseView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request,id=None):

        if id is None:
            expenses= Expense.objects.filter(user=request.user)

            category_id = request.query_params.get('category')
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            min_amount= request.query_params.get('min_amount')
            max_amount= request.query_params.get('max_amount')
            ordering = request.query_params.get('ordering')


            if category_id:

                try:
                    int(category_id)
                except ValueError:
                    return Response({"error": "Category must be an integer"},status=status.HTTP_400_BAD_REQUEST)

                expenses= expenses.filter(category=category_id)

            if start_date:
                try:
                    datetime.strptime(start_date,'%Y-%m-%d')
                except ValueError:
                    return Response({"error": "start_date must be in YYYY-MM-DD format."},status=status.HTTP_400_BAD_REQUEST)
                
                expenses = expenses.filter(created_at__date__gte=start_date)

            if end_date:
                try:
                    datetime.strptime(end_date,'%Y-%m-%d')
                except ValueError:
                    return Response({"error": "end_date must be in YYYY-MM-DD format."},status=status.HTTP_400_BAD_REQUEST)

                expenses = expenses.filter(created_at__date__lte=end_date)

            if min_amount:

                try:
                    float(min_amount)
                except ValueError:
                    return Response({"error": "min_amount must be a number"},status=status.HTTP_400_BAD_REQUEST)

                expenses = expenses.filter(amount__gte=min_amount)

            if max_amount:

                try:
                    float(max_amount)
                except ValueError:
                    return Response({"error": "max_amount must be a number"},status=status.HTTP_400_BAD_REQUEST)
                
                expenses = expenses.filter(amount__lte=max_amount)

            if ordering:
                allowed_fields = ['amount', 'created_at']

                if ordering.lstrip('-') not in allowed_fields:
                    return Response(
                        {"error": "Invalid ordering field."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                expenses = expenses.order_by(ordering)

            paginator = PageNumberPagination()
            paginator.page_size = 2
            page = paginator.paginate_queryset(expenses, request)

            serializer = ExpenseSerializer(page, many=True)

            return paginator.get_paginated_response(serializer.data)

        expense = get_object_or_404(Expense,id=id,user=request.user)
        
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)


    def post(self, request):

        serializer = ExpenseSerializer(data=request.data)

        if serializer.is_valid():

            category= get_object_or_404(Category,id=request.data['category'],user=request.user)

            serializer.save(user=request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


    def put(self,request,id):

        expense = get_object_or_404(Expense,id=id,user=request.user)
                
        serializer = ExpenseSerializer(expense,data=request.data)

        if serializer.is_valid():

            category= get_object_or_404(Category,id=request.data['category'],user=request.user)
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def patch(self,request,id):

        expense = get_object_or_404(Expense,id=id,user=request.user)
                
        serializer = ExpenseSerializer(expense,data=request.data,partial=True)

        if serializer.is_valid():

            if 'category' in request.data:
                category= get_object_or_404(Category,id=request.data['category'],user=request.user)

            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self,request,id):

        expense = get_object_or_404(Expense,id=id,user=request.user)
        expense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class CategoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request,id=None):

        if id is None:

            categories= Category.objects.filter(user=request.user)
            serializer= CategorySerializer(categories,many=True)
            return Response(serializer.data)
            
            

        category= get_object_or_404(Category,id=id,user=request.user)
        serializer=CategorySerializer(category)

        return Response(serializer.data)

    def post(self,request):

        serializer= CategorySerializer(data=request.data)

        if serializer.is_valid():

            serializer.save(user=request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self,request,id):

        category=get_object_or_404(Category,id=id,user=request.user)

        serializer= CategorySerializer(category,data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response (serializer.errors)
        

    def patch(self,request,id):

        category=get_object_or_404(Category,id=id,user=request.user)
        
        serializer= CategorySerializer(category,data=request.data,partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response (serializer.errors)


    def delete(self,request,id):
        category=get_object_or_404(Category,id=id,user=request.user)

        category.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)



class StatisticsView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self,request):

        expenses=Expense.objects.filter(user=request.user)

        total_expenses = expenses.count()
        total_amount = expenses.aggregate(total=Sum('amount'))['total']
        average_expense= expenses.aggregate(average=Avg('amount'))['average']

        if total_amount is None:
            total_amount = 0

        if average_expense is None:
            average_expense=0


        category_stats = (expenses.values(category_name=F('category__name')).annotate(total=Sum('amount')).order_by('-total'))
        monthly_stats=(expenses.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('amount')).order_by('month'))


        category_stats = [
            {
                'category_name': item['category_name'],
                'total': item['total'],
                'percentage': (
                    (item['total'] / total_amount) * 100
                    if total_amount else 0
                )
            }
            for item in category_stats
        ]

        monthly_stats = [
            {
                'month': item['month'].strftime('%Y-%m'),
                'total': item['total']
            }
            for item in monthly_stats
        ]

        return Response({
            'total_expenses': total_expenses,
            'total_amount': total_amount,
            'average_expense':average_expense,
            'by_category': category_stats,
            'monthly': monthly_stats
        })




   

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