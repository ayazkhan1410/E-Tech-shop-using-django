from django.urls import path, include
from . import views

urlpatterns = [
    
    path("", views.home, name='home'),
    path('search_results', views.search_results, name='search_results'),
    
    # add to cart
    path('checkout_cart/<str:slug>', views.checkout_cart, name='checkout_cart'),
    path('remove_cart/<str:slug>', views.remove_cart, name='remove_cart'),
    path('add_to_cart', views.add_to_cart, name='add_to_cart'),
    path('get_cart_data', views.get_cart_data, name='get_cart_data'),
    path('checkout_complete', views.checkout_complete, name='checkout_complete'),
    path('checkout_info', views.checkout_info, name='checkout_info'),
    path('checkout_payment', views.checkout_payment, name='checkout_payment'),
    
    # Payment Failed
    path('payment-failed', views.payment_failed, name='payment-failed'),
    
    #product Detail 
    path('product/', views.product, name='product'),
    
    path('product/<str:company_name>/', views.product_by_company, name='product_by_company'),
    path('product/<str:company_name>/', views.product_by_company_tablets, name='product_by_company_tablets'),
    path('product/<str:company_name>', views.product_by_company_laptops, name='product_by_company_laptops'),
    
    path('category/<int:category_id>/', views.product_by_category, name='product_by_category'),
    path('product_detail/<str:slug>', views.product_detail, name='product_detail'),
    
    path('products/mobile-phones/', views.mobile_phones, name='mobile_phones'),
    path('products/tablets/', views.tablets, name='tablets'),
    path('products/laptops/', views.laptops, name='laptops'),
    
    # Login, logout
    path('register', views.register, name='register'),
    path('login', views.login_page, name='login'),
    path('forget_password', views.forget_password, name='forget_password'),
    path('logout', views.logout_page,name='logout'),
    path('change_password/<token>/', views.change_password, name='change_password'),
    path('reset-password', views.reset_password, name='reset-password'),
    
    # contact us, faq, my account,
    path('contact_us', views.contact_us, name='contact_us'),
    path('faq', views.faq, name='faq'),
    path('my_account', views.my_account, name='my_account'),
    path('about_us', views.about_us, name='about_us'),

    # order tracking
    path('order_tracking', views.order_tracking, name='order_tracking'),
    path('order-progress/<int:pid>/', views.order_progress, name="order_progress"),
    path('order-history', views.order_history, name='order-history'),
    path('cancel-order/<int:pid>/', views.cancel_order, name='cancel-order'),
    path('return-order/<int:pid>/', views.return_order, name='return-order'),
    # new arrival
    path('new-arrival', views.new_arrival, name='new-arrival'),

    
    
    # path('order-progress</int:pid>/', views.order_progress, name='order-progress'),    
    # Mobile Templates
    # path("apple-products", views.apple_products, name='apple-products'),
]