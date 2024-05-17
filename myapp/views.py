from datetime import timedelta, timezone
import http
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render, redirect
from .models import *
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import CustomUser as User
from django.contrib.auth import authenticate, login, logout
import uuid
from .helpers import *
import stripe
from django.conf import settings
import json
from django.http import JsonResponse
from django.db.models import F, ExpressionWrapper, DecimalField
from collections import defaultdict
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
import random
# Create your views here.

def home(request):
    
    category = Category.objects.all()
    
    # Fetch all active mobile Companies
    active_mobile_brands = Product.objects.filter(category__category='Mobile Phones', is_active=True)
    categories = Category.objects.filter(is_active = True)
    
    active_categories = {}
    
    for item in categories:
        active_categories[item.category] = True

        
    
    mobile_companies = set()
    
    # Print all company names associated with mobile products
    for mobile in active_mobile_brands:
        mobile_companies.add(mobile.company.company)
    
    active_tablet_brands = Product.objects.filter(category__category='Tablet', is_active=True)
    tablet_companies = set()
    
    for tablets in active_tablet_brands:
        tablet_companies.add(tablets.company.company)
        
    # taking mobile phones category  and its company brand
    mobile_brand = get_object_or_404(Category, category='Mobile Phones')
    company_brand = Company.objects.filter(category=mobile_brand).order_by('-id')[:6]
        
    # taking tablet category and its company brand
    tablet_brand = get_object_or_404(Category, category='Tablet')
    tab_brand = Company.objects.filter(category=tablet_brand)
    
    # Fetching mobile phone only
    mobiles = Product.objects.filter(category__category='Mobile Phones', is_active=True).order_by('-id')[:6]
        
    # Fetching tablets only
    tablets = Product.objects.filter(category__category='Tablet', is_active=True).order_by('-id')[:6]
    
    # Fetching trending items
    trending_products = Product.objects.filter(is_trending=True, is_active=True).order_by('-id')[:6]
    
    # Fetching Latest Products
    latest_products = Product.objects.filter(is_active=True).order_by('-id')[:4] 
   
    # You might also like section
    product = Product.objects.all()
    
    # shuffle the query
    shuffled_products = list(product)
    random.shuffle(shuffled_products)
    
    
    if request.method == "POST":
        email = request.POST.get('email')
        
        touch = StayInTouch.objects.create(email=email)
        touch.save()
        messages.success(request, 'Your email has been saved successfully')

    context = {
        'company_brand': company_brand,
        'tab_brand': tab_brand,
        
        "mobile_companies": mobile_companies,
        "tablet_companies": tablet_companies,
        
        "trending_products":trending_products,
        
        'tablets':tablets,
        'mobiles':mobiles,
        'latest_products':latest_products,
        
        "active_categories":active_categories
        
        # 'product': product,
    
    }
    
    return render(request, "home.html", context)

def search_results(request):
    return render(request, 'search_results.html')

def calculate_delivery_date(order_date):
    days_to_add = 5  # Number of days for delivery
    current_date = order_date
    while days_to_add > 0:
        current_date += timedelta(days=1)
        if current_date.weekday() not in (5, 6):  # Skip Saturday (5) and Sunday (6)
            days_to_add -= 1
    return current_date

def about_us(request):
    return render(request, 'about_us.html')
@login_required(login_url='login')
# add to cart
def checkout_cart(request, slug):

    product = Product.objects.get(slug=slug)
    user = request.user
    cart_items, created = Cart.objects.get_or_create(user=user, product=product, is_ordered=False)
    
    if created:
        messages.success(request, f"Your {product.product_name} has been added to cart!!")
    else:
        cart_items.quantity += 1
        cart_items.save()
        messages.success(request, f"Another {product.product_name} has been added to cart!!")
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def calculate_cart_item_total(cart_item):

    product = cart_item.product
    cart_item.total_price = float(product.discounted_price()) * cart_item.quantity
    cart_item.save()
    
@login_required(login_url='login')
def add_to_cart(request):
    
    context = {}
    cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
    subtotal = 0
    delivery_date = calculate_delivery_date(timezone.now())

    if request.method == 'POST':
        action = request.POST.get('action')
        cart_item_id = int(request.POST.get('cart_item_id'))
        cart_item = get_object_or_404(Cart, id=cart_item_id)

        if action == 'increase':
            cart_item.quantity += 1
            calculate_cart_item_total(cart_item)
        elif action == 'decrease':
            cart_item.quantity -= 1
            if cart_item.quantity <= 0:
                cart_item.delete()
                return redirect('add_to_cart')
            else:
                calculate_cart_item_total(cart_item)
        else:
            # If action is not increase or decrease, it means a new item is being added to the cart
            # Increase quantity by 1
            cart_item.quantity += 1
            calculate_cart_item_total(cart_item)

        # Recalculate subtotal and total
        subtotal = sum(float(item.total_price) for item in cart_items)
        total = subtotal

        # data = {
        #     'subtotal': subtotal,
        #     'total': total,
        #     'item_total': cart_item.total_price,
        # }

        return redirect('add_to_cart')

    # If not a POST request or action not specified
    for cart_item in cart_items:
        # Calculate total price for each cart item
        calculate_cart_item_total(cart_item)
        subtotal += cart_item.total_price
        
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': subtotal,
        "delivery_date": delivery_date
    }

    return render(request, 'checkout_cart.html', context)

@login_required(login_url='login')
def get_cart_data(request):
    
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
    else:
        cart_items = Cart.objects.none()

    subtotal = sum(float(cart_item.product.discounted_price()) * cart_item.quantity for cart_item in cart_items)
    total = subtotal  # For now, total is same as subtotal

    data = {
        'cart_items': list(cart_items.values()),  # Serialize queryset to JSON-compatible format
        'subtotal': subtotal,
        'total': total,
    }

    return data
@login_required(login_url='login')
def remove_cart(request, slug):
    product = Product.objects.get(slug=slug)
    user = request.user
    
    cart_items = Cart.objects.get(user=user, product=product, is_ordered=False)
    cart_items.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
@login_required(login_url='login')
def checkout_info(request):
    
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        company_name = request.POST.get('company_name')
        area_code = request.POST.get('area_code')
        primary_phone = request.POST.get('primary_phone')
        street_address = request.POST.get('street_address')
        zip_code = request.POST.get('zip_code')
        
        shipping_obj = ShippingAddress.objects.create(
            first_name=first_name,
            last_name=last_name,
            company=company_name,
            area_code=area_code,
            primary_phone=primary_phone,
            street_address=street_address,
            zip_code=zip_code
        )
        shipping_obj.save()
        return redirect('checkout_payment')
        
    return render(request, 'checkout_info.html')
@login_required(login_url='login')
def checkout_payment(request):
    try:
        # Collect necessary data
        email = request.user.email
        cart_items = Cart.objects.filter(user=request.user, is_ordered=False)
        
        # Initialize Stripe with your secret key
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Create line items for each product in the cart
        line_items = []
        for item in cart_items:
            line_items.append({
                'price_data': {
                    'currency': 'pkr',
                    'unit_amount': int(float(item.product.discounted_price()) * 100),
                    'product_data': {
                        'name': item.product.product_name,  # Name of the product
                    },
                },
                'quantity': item.quantity,  # Quantity of the product
            })

        # Create a Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,  # Provide the line items data here
            mode='payment',
            success_url='http://127.0.0.1:8082/checkout_complete',
            cancel_url='http://127.0.0.1:8082/payment-failed',
        )

        # Check if the session was created successfully
        if session:
            for item in cart_items:
                OrderTracking.objects.create(
                    user=request.user,
                    product=item.product,
                    quantity=item.quantity,
                    total_price=item.total_price,
                    order_status=2,  # Placed
                )
                
            item.mark_as_ordered_or_deleted()
            item.delete()
            
            return redirect(session.url)
  
    except Exception as e:
        print(e)
        messages.error(request, 'An error occurred while processing the payment. Please try again.')

    # If an error occurs or session creation fails, redirect back to the checkout page
    return redirect('checkout_payment')
@login_required(login_url='login')
def checkout_complete(request):
    # Retrieve all ordered items for the current user
    ordered_items = OrderTracking.objects.filter(user=request.user)
    delivery_date = calculate_delivery_date(timezone.now())

    context = {
        'ordered_items': ordered_items,
        'delivery_date': delivery_date
    }

    return render(request, 'checkout_complete.html', context)

def contact_us(request):
    contact = Contact.objects.all()
    if request.method == 'POST':
        
       name = request.POST.get('name')
       email = request.POST.get('email')
       subject = request.POST.get('subject')
       message = request.POST.get('message')
       contact = contact.create(name=name, email=email, subject=subject, message=message)
       contact.save()
       
       messages.info(request, 'Your message has been sent successfully')
       return redirect('contact_us')
       
    return render(request, 'contact_us.html')
@login_required(login_url='login')
def payment_failed(request):
    return render(request, 'payment-failed.html')
@login_required(login_url='login')
def faq(request):
    return render(request, 'faq.html')
@login_required(login_url='login')
def my_account(request):
    return render(request, 'my_account.html')

def product_detail(request, slug):
    # Retrieve the product by slug
    product = get_object_or_404(Product, slug=slug)
    product_description = ProductDescription.objects.filter(product=product)
    product_img = ProductDescription.objects.filter(product=product)
    information = AdditionalInformation.objects.filter(product=product)
    reviews = Review.objects.filter(product=product)
    review_count = reviews.count()

    # Shuffle and get random products
    products = Product.objects.all()
    shuffled_products = list(products)
    random.shuffle(shuffled_products)
    random_products = shuffled_products[:6]

    new_product_name = None
    if information:
        new_product_name = information[0].new_product_name

    if request.method == 'POST':
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, 'You need to log in to submit a review.')
            return redirect('login')  # Redirect to login page

        # Check if the user has purchased the product
        user_purchased = Review.objects.filter(user=request.user, product=product).exists()
        if not user_purchased:
            messages.error(request, 'You can only review products you have purchased.')
            return redirect('product_detail', slug=slug)

        # If the user is authenticated and has purchased the product, proceed with review submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        rating = int(request.POST.get('rating'))

        rating_obj = Review.objects.create(
            product=product,
            user=request.user,
            name=name,
            title=email,
            review=message,
            rating=rating,
        )
        rating_obj.save()

        messages.success(request, 'Your review has been submitted successfully')
        return redirect('product_detail', slug=slug)

    # Check if the user is authenticated to filter their reviews
    user_reviews = None
    if request.user.is_authenticated:
        user_reviews = Review.objects.filter(user=request.user, product=product)

    context = {
        'product': product,
        'product_description': product_description,
        'product_img': product_img,
        'information': information,
        'new_product_name': new_product_name,
        'review_count': review_count,
        'reviews': reviews,
        'user_reviews': user_reviews,
        'random_products': random_products,
    }

    return render(request, 'product_detail.html', context)

def product(request):
    
    total_products = Product.objects.all().count()
    all_products = Product.objects.all()

    category_count  = {}
    
    for item in all_products:
        category = item.category.category
        if category not in category_count:
            category_count[item.company.company] = 1
        else:
            category_count[item.company.company] += 1
            
    # Calculate counts of products for each company
    company_counts = {}
    for product in all_products:
        company_name = product.company.company
        if company_name not in company_counts:
            company_counts[company_name] = 1
        else:
            company_counts[company_name] += 1
    
    paginator = Paginator(all_products, 9)
    page_number = request.GET.get('page')

    try:
        paginated_products = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        price_from = request.POST.get('price_from')
        price_to = request.POST.get('price_to')
        search = request.POST.get('search')
        company_name = request.POST.get('company_name')
        
        
        # Filter products based on company
        if company_name:
            all_products = all_products.filter(company__company=company_name)
            paginator = Paginator(all_products, 9)
            paginated_products = paginator.page(1)  # Reset page to 1 after filtering

        # Check if price_from and price_to are provided and convert them to integers
        if price_from and price_to:
            # Filter products based on price range
            all_products = all_products.annotate(
                discounted_price=F('orignal_price') - F('orignal_price') * F('discount_percentage') / 100
            ).filter(
                # Filter products where discounted price is within the specified range
                discounted_price__gte=price_from,
                discounted_price__lte=price_to
            )

        # Filter products based on search query
        if search:
            all_products = all_products.filter(Q(product_name__icontains=search) | Q(product_description__icontains=search))

        # Re-paginate the queryset after applying filters
        paginator = Paginator(all_products, 9)
        paginated_products = paginator.page(1)  # Reset page to 1 after filtering

    context = {
        'product_names': paginated_products,
        "total_products": total_products,
        "mobile_companies": category_count,
        'show_top_companies': True,
        'company_counts': company_counts

    }

    return render(request, 'product.html', context)

def new_arrival(request):
    seven_days_ago = timezone.now() - timedelta(days=7)
    new_arrivals = Product.objects.filter(created_at__gte=seven_days_ago)
            
    paginator = Paginator(new_arrivals, 9)
    page_number = request.GET.get('page')

    try:
        paginated_products = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)
        
    context = {
        'new_arrivals': paginated_products,
        
    }
    
    return render(request, 'new-arrival.html', context)
@login_required(login_url='login')
def product_by_category(request, category_name):

    category_products = Product.objects.filter(category__category=category_name)
    
    paginator = Paginator(category_products, 9)
    page_number = request.GET.get('page')
    
    try:
        paginated_products = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)
    
    total_products = category_products.count()
    print("Total Products: ", total_products)
    
    context = {
        'product_names': paginated_products,
        "category_name": category_name,
        "total_products": total_products,  
        'show_top_companies': False,  

        
    }
    return render(request, 'product.html', context)
@login_required(login_url='login')
def product_by_company(request, company_name):
    
    # Filter products based on the company name
    company_products = Product.objects.filter(company__company=company_name)   
    total_products = company_products.count()
    
    paginator = Paginator(company_products, 9)
    page_number = request.GET.get('page')
    
    try:
        paginated_products = paginator.page(page_number)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)
        
    context = {
        'product_names': paginated_products,
        "company_name": company_name,
        "total_products":total_products
    }
    
    return render(request, 'product.html', context)
@login_required(login_url='login')
def product_by_company_tablets(request, company_name=None):
        
        # Filter products based on the company name
        tablets_products = Product.objects.filter(company__company=company_name)   
                   
        paginator = Paginator(tablets_products, 9)
        page_number = request.GET.get('page')
        
        try:
            paginated_products = paginator.page(page_number)
        except PageNotAnInteger:
            paginated_products = paginator.page(1)
        except EmptyPage:
            paginated_products = paginator.page(paginator.num_pages)
        
        context = {
            'product_names': paginated_products,
            "company_name": company_name,
        }
        
        return render(request, 'product.html', context)
@login_required(login_url='login')
def order_tracking(request):
    
    delivery_date = calculate_delivery_date(timezone.now())
    
    if request.method == "POST":
        order_id = request.POST.get('order_id')
        
        cart_items = OrderTracking.objects.filter(user=request.user, order_id=order_id)
        
        if not cart_items.exists():
            messages.error(request, 'Order ID does not exist')
            return redirect('order_tracking')
        
        context = {
            'cart_items': cart_items,
            "delivery_date":delivery_date
        }
        return render(request, 'order-status.html', context)  
    
    return render(request, 'order_tracking.html')

def login_page(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not User.objects.filter(email= email).exists():
            messages.info(request,'Please Create Account first')
            return redirect('login')
        user = authenticate(email=email, password=password)
        if user is None:
            messages.info(request, 'Invalid Password')
            return redirect('login')
        else:
            login(request, user)
            return redirect('home')              
    return render(request, 'login.html')

def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        profile_photo = request.FILES.get('profile_photo')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        
        user = User.objects.filter(email=email)
        if user.exists():
            messages.info(request, 'Email already exists')
            return redirect('register')
        else:
            user = User.objects.create_user(email=email, first_name=first_name, last_name=last_name, user_profile=profile_photo, password=password)
            user.set_password(password)
            user.save()
            messages.info(request, 'Account created successfully')
            return redirect('login')
    return render(request, 'register.html')
def forget_password(request):
    
    try:
      if request.method == "POST":
          email = request.POST.get('email')
          
          if not User.objects.filter(email = email).exists():
              messages.info(request, 'Email does not exists')
              return redirect("forget_password")
          
          user_obj = User.objects.get(email=email)
          token = str(uuid.uuid4())
            
          profile_obj, created = Profile.objects.get_or_create(user=user_obj)
          profile_obj.forget_token = token
          profile_obj.save()  
          send_email(user_obj.email, token)  
          messages.success(request, 'An email has been sent.')
          return redirect('forget_password')
      
    except Exception as e:
        print(e)
        
    return render(request, 'forget_password.html')
def change_password(request, token):
    
    # Retrieve the Profile object associated with the provided token
    profile_obj = Profile.objects.filter(forget_token=token).first()
    
    # Check if the request method is POST
    if request.method == "POST":
        # Retrieve the password and confirm_password from the POST data
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Check if the password matches the confirm_password
        if password != confirm_password:
            # If passwords don't match, display a message and redirect back to the change password page
            messages.info(request, 'Password does not match')
            return redirect(f'change_password{token}')
        else:
            # Retrieve the User object associated with the profile's email
            user_obj = User.objects.get(email=profile_obj.user.email)
            
            # Set the new password for the user
            user_obj.set_password(password)
            
            # Save the user object with the new password
            user_obj.save()
            
            # Display a success message and redirect to the login page
            messages.info(request, 'Password has been changed successfully')
            return redirect('login')        
    return render(request, 'change_password.html')

def reset_password(request):
    if request.method == "POST":
        old_password = request.method.POST('old_passowrd')
        new_password1 = request.method.POST('new_password1')
        new_password2 = request.method.POST('new_password2')
        
        
    return render(request, 'reset-password.html')
@login_required(login_url='login')

def order_progress(request, pid):
    order = OrderTracking.objects.get(id = pid)
    orderstatus = status
    return render(request, 'order-progress.html', locals())
@login_required(login_url='login')

def order_history(request):
    
    order = OrderTracking.objects.filter(user=request.user)
    
    return render(request, 'order-history.html', locals())

def logout_page(request):
    logout(request)
    return redirect('home')


        