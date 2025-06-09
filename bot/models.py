
from django.db import models


# Create your models here.



class User(models.Model):
    LANG_CHOICES = (
        ('ru', 'Russian'),
        ('uz','Uzbek')
    )
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    tg_id = models.BigIntegerField(unique=True)
    role=models.CharField(max_length=5,choices=ROLE_CHOICES,default='user')
    address=models.CharField(max_length=255,null=True,blank=True)
    user_number=models.CharField(null=True,blank=True,max_length=13)
    lang=models.CharField(max_length=2,choices=LANG_CHOICES,null=True,blank=True)

    def __str__(self):
        return self.lang

class Category(models.Model):
    name = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='products')
    title = models.CharField(max_length=100)
    title_ru = models.CharField(max_length=100)
    image=models.ImageField(upload_to='products/',null=True,blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    description = models.TextField(null=True,blank=True)
    description_ru=models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def image_url(self):
        if self.image:
            return f"https://suvbackend-production.up.railway.app/{self.image.url}"
        return '/static/images/no-image.jpg'
    def __str__(self):
        return self.title

class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='cart')
    products = models.ManyToManyField(Product,through='CartItem')

class Order(models.Model):
    STATUS_ORDER_UZ = (
        ('new', "Yangi"),
        ('delivered', "Yetkazilgan"),
        ('pending', "Kutilmoqda"),
    )

    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='orders')
    products = models.ManyToManyField(Product, through='OrderItem')
    status=models.CharField(max_length=255,choices=STATUS_ORDER_UZ,default='new')

    @property
    def status_ru(self):
        return {
            'new': 'Новый',
            'delivered': 'Доставлено',
            'pending': 'Ожидается'
        }.get(self.status, self.status)





class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def price(self):
        return self.product.price
    @property
    def total(self):
        return self.quantity * self.price



class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def price(self):
        return self.product.price
    @property
    def total(self):
        return self.quantity * self.price


class Bonus(models.Model):
    content = models.TextField()
    content_ru = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.content