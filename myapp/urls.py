from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path('search_results', views.search_results, name='search_results'),
    path('about_us', views.about_us, name='about_us'),
    
    # add to cart
    path('checkout_cart/<str:slug>', views.checkout_cart, name='checkout_cart'),
    path('remove_cart/<str:slug>', views.remove_cart, name='remove_cart'),
    path('add_to_cart', views.add_to_cart, name='add_to_cart'),
    path('get_cart_data', views.get_cart_data, name='get_cart_data'),
    
    
    path('checkout_complete', views.checkout_complete, name='checkout_complete'),
    path('checkout_info', views.checkout_info, name='checkout_info'),
    path('checkout_payment', views.checkout_payment, name='checkout_payment'),
    path('contact_us', views.contact_us, name='contact_us'),
    path('faq', views.faq, name='faq'),
    path('my_account', views.my_account, name='my_account'),
    path('product_detail/<str:slug>', views.product_detail, name='product_detail'),
    path('product', views.product, name='product'),
    path('order_tracking', views.order_tracking, name='order_tracking'),
    path('login', views.login_page, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout_page,name='logout'),
    path('forget_password', views.forget_password, name='forget_password'),
    path('change_password/<token>/', views.change_password, name='change_password'),
]