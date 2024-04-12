from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,Category
from cart.forms import CartAddProductForm
from cart.cart import Cart
# Create your views here.


def product_list(request,category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    cart_add_product = CartAddProductForm()
    cart = Cart(request)
    if category_slug :
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(Category=category)
    context = {'category':category, 'categories':categories ,'products':products , 'form':cart_add_product,'cart':cart} 
    return render(request, 'shop/index.html',context)
    
def product_detail(request,id,slug):
    product = get_object_or_404(Product,id=id, slug=slug , available=True)
    cart_add_product = CartAddProductForm()
    cart = Cart(request)
    context = {'product':product , 'form':cart_add_product,'cart':cart}
    return render(request, 'shop/product/detail.html' , context)


# def index_view(request):
#     return render(request,'shop/index.html')

def test(request):
    return render(request,'orders/ppdf.html')