from django.http import HttpResponseRedirect
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
from django.conf import settings

# Create your views here.

def home(request):
    category = Category.objects.all()
    product = Product.objects.all()
    
    # taking mobile phones category  and its company brand
    mobile_brand = get_object_or_404(Category, category='Mobile Phones')
    company_brand = Company.objects.filter(category=mobile_brand)
    
    # taking tablet category and its company brand
    tablet_brand = get_object_or_404(Category, category='Tablet')
    tab_brand = Company.objects.filter(category=tablet_brand)

    
    # trending_items = Product.objects.filter(is_trending=True)
    
    paginator = Paginator(product, 6)  # Assuming 6 items per page

    try:
        product1 = paginator.get_page(paginator)
    except PageNotAnInteger:
        product1 = paginator.get_page(1)
    except EmptyPage:
        product1 = paginator.page(paginator.num_pages)

    context = {
        'category': category,
        'product': product,
        'product1':product1,
        'company_brand': company_brand,
        'tab_brand': tab_brand,
       
    }
    
    return render(request, "home.html", context)

def search_results(request):
    return render(request, 'search_results.html')

def about_us(request):
    return render(request, 'about_us.html')

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
   
import json
from django.http import JsonResponse

def add_to_cart(request):    
    context = {}
    cart_items = Cart.objects.all()  # Fetch cart items as needed
    subtotal = 0
 
    if request.method == 'POST':
        
        action = request.POST.get('action')
        cart_item_id = int(request.POST.get('cart_item_id'))
        cart_item = Cart.objects.get(id=cart_item_id)
      
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1

        cart_item.total_price = float(cart_item.product.discounted_price()) * cart_item.quantity
        cart_item.save()

        # Calculate subtotal and total
        subtotal = sum(float(cart_item.product.discounted_price()) * cart_item.quantity for cart_item in cart_items)
        total = subtotal  # For now, total is same as subtotal

        # Prepare data for JSON response
        data = {
            'subtotal': subtotal,
            'total': total,
            'item_total': cart_item.total_price,  # Total price of the updated item
        }

        return JsonResponse(data)

    # If not a POST request or action not specified
    for cart_item in cart_items:
        cart_item.total_price = float(cart_item.product.discounted_price()) * cart_item.quantity
        subtotal += cart_item.total_price

    context = {'cart_items': cart_items, 'subtotal': subtotal, 'total': subtotal}
    
    return render(request, 'checkout_cart.html', context)

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

    return JsonResponse(data)

def remove_cart(request, slug):
    product = Product.objects.get(slug=slug)
    user = request.user
    cart_items = Cart.objects.get(user=user, product=product, is_ordered=False)
    cart_items.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def checkout_complete(request):
    return render(request,'checkout_complete.html')

def checkout_info(request):
    return render(request, 'checkout_info.html')

def checkout_payment(request):
    return render(request, 'checkout_payment.html')

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

def faq(request):
    return render(request, 'faq.html')

def my_account(request):
    return render(request, 'my_account.html')

def product_detail(request, slug):
   
    product = Product.objects.get(slug = slug)
    product_description = ProductDescription.objects.filter(product=product)
    product1 = Product.objects.filter(is_trending=True)
    product_img = ProductDescription.objects.filter(product=product)
    information = AdditionalInformation.objects.filter(product=product)
    new_product_name = None
    if information:
        new_product_name = information[0].new_product_name
   

    paginator = Paginator(product1, 6)  # Assuming 6 items per page
    try:
        product1 = paginator.get_page(paginator)
    except PageNotAnInteger:
        product1 = paginator.get_page(1)
    except EmptyPage:
        product1 = paginator.page(paginator.num_pages)
        
    context = {
        'product': product,
        'product1': product1,
        'product_description': product_description,
        'product_img': product_img,
        'information':information,
       'new_product_name':new_product_name
    }
    return render(request, 'product_detail.html', context)

def product(request):
    return render(request, 'product.html')

def order_tracking(request):
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

def logout_page(request):
    logout(request)
    return redirect('home')