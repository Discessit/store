from django.urls import path
from .views import ProductListView, CartView, add_to_cart, remove_from_cart, CheckoutView, OrderHistoryView, OrderDetailView
from django.views.generic import TemplateView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    #Корзина
    path('cart/', CartView.as_view(), name='cart_view'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    #Заказ
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('order-history/', OrderHistoryView.as_view(), name='order_history'),
    path('cart/checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-success/', TemplateView.as_view(template_name='order_success.html'), name='order_success'),
    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='change_password'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]
