from django.db import models
from shop.models import Product
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class Order(models.Model):
    first_name = models.CharField(_('first name'),max_length=200 )
    last_name = models.CharField(_('last name'),max_length=200)
    email = models.EmailField(_('e_mail'),max_length=255)
    address = models.TextField(_('address'))
    city = models.CharField(_('city'),max_length=200)
    country = models.CharField(_('country'),max_length=200)
    zip_code = models.CharField(_('zip code'),max_length=15)
    telephone = models.CharField(_('telephone'),max_length=20)
    created = models.DateTimeField(_('created'),auto_now_add=True)
    updated = models.DateTimeField(_('updated'),auto_now=True)
    paid = models.BooleanField(_('paid'),default=False)
    
    class Meta:
        ordering = ('-created',)
        
    def __str__(self) :
        return f'Order {self.id}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items',on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items',on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self) :
        return str(self.id)
    
    def get_cost(self):
        return self.price*self.quantity
    
    