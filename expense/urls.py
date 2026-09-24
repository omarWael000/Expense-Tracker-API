
from django.urls import path
from .views import ExpenseView,UserRegistrationView,LoginView,CategoryView

urlpatterns = [
    path('expenses/',ExpenseView.as_view(),name='expenses'),
    path('expenses/<int:id>/', ExpenseView.as_view(), name='expense-detail'),
    path('users/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('categories/',CategoryView.as_view(), name='categories'),
    path('categories/<int:id>/', CategoryView.as_view(), name='category-detail'),


]