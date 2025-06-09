from django.contrib import admin
from bot.models import Order,OrderItem,Product,Category,User,Bonus

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(Bonus)