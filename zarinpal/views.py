# from django.shortcuts import render,get_object_or_404
from orders.models import Order
# # Create your views here.

from django.conf import settings
from .tasks import payment_completed
# import requests
# import json


# # sandbox merchant 
# if settings.SANDBOX:
#     sandbox = 'sandbox'
# else:
#     sandbox = 'www'


# ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
# ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
# ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"

# amount = 1000  # Rial / Required
# description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
# phone = ""  # Optional
# # Important: need to edit for realy server.
# CallbackURL = 'http://127.0.0.1:8080/zarinpal/verify/'


# def send_request(request):
#     order_id = request.session.get('order_id')
#     order = get_object_or_404(Order,id=order_id)
#     total_cost = order.get_total_cost()
#     data = {
#         "MerchantID": settings.MERCHANT,
#         "Amount": total_cost,
#         "Description": description,
#         "Phone": order.telephone,
#         "Email":order.email,
#         "CallbackURL": CallbackURL,
#     }
#     data = json.dumps(data)
#     # set content length by data
#     headers = {'content-type': 'application/json', 'content-length': str(len(data)) }
#     try:
#         response = requests.post(ZP_API_REQUEST, data=data,headers=headers, timeout=10)

#         if response.status_code == 200:
#             response = response.json()
#             if response['Status'] == 100:
#                 return {'status': True, 'url': ZP_API_STARTPAY + str(response['Authority']), 'authority': response['Authority']}
#             else:
#                 return {'status': False, 'code': str(response['Status'])}
#         return response
    
#     except requests.exceptions.Timeout:
#         return {'status': False, 'code': 'timeout'}
#     except requests.exceptions.ConnectionError:
#         return {'status': False, 'code': 'connection error'}


# def verify(authority):
#     data = {
#         "MerchantID": settings.MERCHANT,
#         "Amount": amount,
#         "Authority": authority,
#     }
#     data = json.dumps(data)
#     # set content length by data
#     headers = {'content-type': 'application/json', 'content-length': str(len(data)) }
#     response = requests.post(ZP_API_VERIFY, data=data,headers=headers)

#     if response.status_code == 200:
#         response = response.json()
#         if response['Status'] == 100:
#             return {'status': True, 'RefID': response['RefID']}
#         else:
#             return {'status': False, 'code': str(response['Status'])}
#     return response
from django.shortcuts import render , get_object_or_404
from orders.models import Order
# Create your views here.
from django.http import HttpResponse
from django.shortcuts import redirect
from zeep import Client


client = Client('https://sandbox.zarinpal.com/pg/services/WebGate/wsdl')
amount = 1000  # Toman / Required
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
mobile = '09123456789'  # Optional
CallbackURL = 'http://localhost:8000/zarinpal/verify/' # Important: need to edit for realy server.

def send_request(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order,id=order_id)
    total_cost = order.get_total_cost()
    result = client.service.PaymentRequest(settings.MERCHANT, total_cost, description, order.email, "mobile", CallbackURL)
    if result.Status == 100:
        return redirect('https://sandbox.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        return HttpResponse('Error code: ' + str(result.Status))

def verify(request):
    if request.GET.get('Status') == 'OK':
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order,id=order_id)
        result = client.service.PaymentVerification(settings.MERCHANT, request.GET['Authority'], amount)
        if result.Status == 100:
            order.paid = True
            order.save()
            payment_completed.delay(order.id)
            # return HttpResponse('Transaction success.\nRefID: ' + str(result.RefID))
            return render(request,"zarinpal/success.html",{"id":result.RefID})
        elif result.Status == 101:
            # return HttpResponse('Transaction submitted : ' + str(result.Status))
            return render(request,"zarinpal/submitted.html",{"status":result.Status})
        else:
            # return HttpResponse('Transaction failed.\nStatus: ' + str(result.Status))
            return render(request,"zarinpal/failed.html",{"status":result.Status})
    else:
        # return HttpResponse('Transaction failed or canceled by user')
        return render(request,"zarinpal/canceled.html",{})