# Create your views here.
# Import necessary classes
import datetime
import string
from random import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from .forms import OrderForm, InterestForm, LoginForm, Password_ResetForm, RegisterForm
from .models import Category, Product, Client, Order
from django.shortcuts import get_object_or_404, render, redirect
from datetime import date
from django.contrib import messages


def index(request):
    if request.user.is_authenticated and 'last_login' in request.session:
        last_login = request.session['last_login']
        print("user_last_login: ", last_login)
        msg = "Your last login was: " + str(last_login)
    else:
        msg = "Your last login was more than an hour ago!!"

    cat_list = Category.objects.all().order_by('id')[:10]
    return render(request, 'myaoo/index.html', {'cat_list': cat_list, 'msg': msg})


def about(request):
    visits = request.COOKIES.get('about_visits')
    if visits:
        response = render(request, 'myaoo/about.html', {'about_visits': visits})
        about_visits = int(visits) + 1
        response.set_cookie('about_visits', about_visits, expires=100)
    else:
        response = render(request, 'myaoo/about.html', {'about_visits': 1})
        response.set_cookie('about_visits', 1, expires=300, )

    return response


@login_required
def detail(request, cat_no):
    response = HttpResponse()
    categories = Category.objects.filter(id=cat_no).values()
    if not categories:
        response.write(get_object_or_404(categories))
        return response
    products = Product.objects.filter(category=cat_no)
    return render(request, 'myaoo/detail.html', {'cat_name': categories[0].get('warehouse'), 'products': products})


@login_required
def products(request):
    prodlist = Product.objects.all().order_by('id')[:10]
    return render(request, 'myaoo/products.html', {'prodlist': prodlist})


@login_required
def place_order(request):
    msg = ''
    prodlist = Product.objects.all()
    if request.method == 'POST':
        form = OrderForm(request.POST, initial={'status_date': date.today(), 'order_status': 'Order Placed'})
        if form.is_valid():
            order = form.save(commit=False)
            if order.num_units <= order.product.stock:
                order.product.stock = int(order.product.stock) - 1
                product = Product.objects.get(pk=order.product.id)
                product.stock = product.stock - order.num_units
                product.save()
                order.save()
                msg = 'Your order has been placed successfully'
            else:
                msg = 'We do not have sufficient stock to fill your order.'
            return render(request, 'myaoo/order_response.html', {'msg': msg})

    else:
        form = OrderForm()
    return render(request, 'myaoo/placeorder.html', {'form': form, 'msg': msg, 'prodlist': prodlist})


@login_required
def productdetail(request, prod_id):
    prod = Product.objects.get(pk=prod_id)
    if request.method == 'POST':
        form = InterestForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['interested'] == 'Yes':
                prod.interested = prod.interested + 1
                print(prod.id)
                prod.save()
                return redirect('/myaoo/')
            else:
                return redirect('/myaoo/')
    else:
        form = InterestForm()
    return render(request, 'myaoo/productdetail.html', {'form': form, 'prod': prod})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                current_time = datetime.datetime.now()
                request.session['last_login'] = str(current_time)
                request.session.set_expiry(60 * 60)
                return HttpResponseRedirect(reverse('myaoo:index'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        return render(request, 'myaoo/login.html', {'LoginForm': LoginForm})


@login_required
def user_logout(request):
    try:
        logout(request)
        return HttpResponseRedirect('../login')
    except:
        return HttpResponse("Please login first!")


@login_required
def myorders(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        user_db = User.objects.get(id=user_id)
        try:
            if_exists = User.objects.get(username=user_db)
            if user_db:
                name = list(Order.objects.filter(client=user_db))
            else:
                msg = "There are no available orders!"
                return render(request, 'myaoo/order_response.html', {"msg": msg})
        except:
            msg = "You are not a registered client!"
            return render(request, 'myaoo/order_response.html', {"msg": msg})

        try:
            img_url = Client.objects.get(username=user_db).profile_photo.url
        except:
            img_url = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png"
        return render(request, 'myaoo/myorders.html', {'order_list': name, 'img_url': img_url})
    else:
        return redirect('myaoo:login')


def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        company = request.POST.get('company')
        shipping_address = request.POST.get('shipping_address')
        city = request.POST.get('city')
        province = request.POST.get('province')
        photo = request.FILES['photo'] if 'photo' in request.FILES else None
        interested = request.POST.getlist('interested')
        interested_in = []
        for i in interested:
            interested_in.append(Category.objects.get(id=i))

        if User.objects.filter(username=username).exists():
            return HttpResponse('Username already exists.')
        else:
            if User.objects.filter(email=email).exists():
                return HttpResponse('Email already exists.')
            else:
                client = Client(username=username, password=password, email=email,
                                company=company, shipping_address=shipping_address, city=city,
                                province=province, profile_photo=photo)
                client.save()
                client.interested_in.add(*interested_in)
                client.save()

                user = User.objects.get(username=username)
                user.first_name = firstname
                user.last_name = lastname
                user.set_password(password)
                user.save()

        return redirect('myaoo:login')
    else:
        if request.user.is_authenticated:
            return redirect('myaoo:myorders')
        register_form = RegisterForm()
        return render(request, 'myaoo/register.html', {'form': register_form})


def password_reset(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = User.objects.filter(email=email)
        print(user)
        if user:
            user = user[0]
            new_password = "shivani123"
            # new_password = generate_password()
            user.set_password(new_password)
            user.save()

            print(new_password)

            # Email settings
            subject = "New Password"
            # email_template_name = "myaoo/password_reset_email.txt"
            c = {
                "email": user.email,
                'domain': '127.0.0.1:8000',
                'site_name': 'Website',
                "user": user,
                'protocol': 'http',
                'new_password': new_password,
            }
            # email = render_to_string(email_template_name, c)
            try:
                send_mail(subject, "Password reset done. Your new password is "+new_password, 'shivanipwork@gmail.com', [user.email], fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')

            return redirect('myaoo:password_reset_done', 1)
        else:
            return redirect('myaoo:password_reset_done', 0)
    else:
        if request.user.is_authenticated:
            return redirect('myaoo:myorders')
        password_reset_form = Password_ResetForm()
        return render(request, 'myaoo/password_reset.html', {'form': password_reset_form})


def generate_password():
    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
    password_length = 8
    random.shuffle(characters)

    password = []
    for i in range(password_length):
        password.append(random.choice(characters))

    random.shuffle(password)
    return "".join(password)


def password_reset_done(request, done):
    return render(request, 'myaoo/password_reset_done.html', {'done': done})


def json(request):
    data = list(Category.objects.values())
    return JsonResponse(data, safe=False)
