from django.contrib import admin
from .models import Product, Category, Client, Order

admin.site.register(Category)
admin.site.register(Order)

@admin.action(description='Add 50 to the current stock value of selected products')
def add50(modeladmin, request, queryset):
    for p in queryset:
        p.stock += 50
        if p.stock > 1000:
            p.stock = 1000
        p.save()


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'available')
    actions = [add50]


admin.site.register(Product, ProductAdmin)


class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'city', 'interests')

    @staticmethod
    def interests(obj):
        return "\n".join([p.name for p in obj.interested_in.all()])


admin.site.register(Client, ClientAdmin)
