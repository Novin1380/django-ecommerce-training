from django.shortcuts import render,redirect,get_object_or_404
from .forms import OrderCreateform
from .models import OrderItem,Order
from cart.cart import Cart
from .tasks import order_created
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
import weasyprint
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from coupons.forms import CouponApplyForm
# Create your views here.

def order_create(request):
    cart = Cart(request)
    coupon_apply_form = CouponApplyForm()
    if request.method == 'POST':
        form = OrderCreateform(request.POST)
        
        if form.is_valid():
            order = form.save()
            for item in cart :
                OrderItem.objects.create(order=order,product=item['product'],price=item['price'],quantity=item['quantity'])
            cart.clear()
            order_created.delay(order.id)
            # return render(request, 'orders/created.html',{'order': order})
            request.session['order_id'] = order.id
            return redirect(reverse('zarinpal:request'))
    else :
        form = OrderCreateform()
    return render(request, 'orders/create.html',{'form': form,'cart': cart , "coupon_apply_form":coupon_apply_form}) 

@staff_member_required
def admin_order_detail(request,order_id):
    order = get_object_or_404(Order , id=order_id)
    return render(request , "admin/orders/detail.html",{'order':order})

@staff_member_required
def admin_order_pdf(request,order_id):
    order = get_object_or_404(Order , id=order_id)
    html = render_to_string("orders/ppdf.html",{'order':order})
    # stylesheets = [weasyprint.CSS(settings.STATIC_ROOT+'css/invoice.css')]
    response = HttpResponse(content_type='application/pdf')
    response["Content-Disposition"] = f'filename=order_{order.id}.pdf'
    #THIS WORKS WITH MY SETTINGS
    weasyprint.HTML(string=html).write_pdf(response,stylesheets=[weasyprint.CSS('static/css/invoice.css')])
    # weasyprint.HTML(string=html).write_pdf(response,stylesheets)
    # weasyprint.HTML(string=html).write_pdf(response)
    #THIS IS FOR OS SETTINGS
    # weasyprint.HTML(string=html).write_pdf(response,stylesheets=[weasyprint.CSS(settings.STATIC_ROOT+'css/invoice.css')])
    return response