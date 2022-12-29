# from django.urls import path
# from myaoo import views
# import include
# app_name = 'myaoo'
# urlpatterns = [
#  path(r'', views.index, name='index'),
#  path(r'myaoo/', include('myaoo.urls')),
#  ]

from django.urls import path
from myaoo import views
from django.conf.urls.static import static

from mysiteF22 import settings

app_name = 'myaoo'

urlpatterns = [
 path('json', views.json, name='json'),
 path(r'', views.index, name='index'),
 path(r'about/', views.about, name='about'),
 path(r'<int:cat_no>/', views.detail, name='Category'),
 path(r'products/', views.products, name='products'),
 path(r'placeorder/', views.place_order, name='placeorder'),
 path(r'products/<int:prod_id>/', views.productdetail, name='productdetail'),
 path(r'login/', views.user_login, name='login'),
 path(r'logout/', views.user_logout, name='logout'),
 path(r'myorders/', views.myorders, name='myorders'),
 path(r'register/', views.user_register, name="register"),
 path('password_reset/', views.password_reset, name='password_reset'),
 path('password_reset/<int:done>/', views.password_reset_done, name='password_reset_done')] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


