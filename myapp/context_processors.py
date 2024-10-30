# store/context_processors.py

from .models import Category, Product, Company
import random

def global_store_context(request):
    categories = Category.objects.filter(is_active=True)
    
    mobiles = Product.objects.filter(category__category='Mobile Phones', is_active=True).order_by('-id')[:6]
    laptops = Product.objects.filter(category__category='Laptops', is_active=True).order_by('-id')[:6]
    trending_products = Product.objects.filter(is_trending=True, is_active=True).order_by('-id')[:6]
    
    # Shuffle products to display randomly
    all_products = list(Product.objects.all())
    random.shuffle(all_products)
    shuffled_products = all_products[:6]

    return {
        'categories': categories,
        'mobiles': mobiles,
        'laptops': laptops,
        'trending_products': trending_products,
        'shuffled_products': shuffled_products,
    }
