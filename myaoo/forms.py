from django import forms
from myaoo.models import Order, Client, Product, User, Category
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['client', 'product', 'num_units']

    client = forms.ModelChoiceField(widget=forms.RadioSelect, queryset=Client.objects.all(), to_field_name="username",
                                    label='Client name')
    product = forms.ModelChoiceField(queryset=Product.objects.all().order_by('id'), to_field_name="name")
    num_units = forms.IntegerField(label='Quantity')


class InterestForm(forms.Form):
    INT_CHOICES = [('Yes', 'Yes'), ('No', 'No')]
    interested = forms.ChoiceField(widget=forms.RadioSelect, choices=INT_CHOICES)
    quantity = forms.IntegerField(initial=1, min_value=1)
    comments = forms.CharField(widget=forms.Textarea, label='Additional Comments', required=False)


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class RegisterForm(forms.Form):
    PROVINCE_CHOICES = [
        ('AB', 'Alberta'),
        ('MB', 'Manitoba'),
        ('ON', 'Ontario'),
        ('QC', 'Quebec'), ]

    username = forms.CharField(required=True, label="Username")
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(required=True, widget=forms.PasswordInput, label="Password")
    firstname = forms.CharField(required=True, label="First Name")
    lastname = forms.CharField(required=False, label="Last Name")
    company = forms.CharField(required=True, label="Company")
    shipping_address = forms.CharField(required=True, label="Shipping Address")
    city = forms.CharField(required=True, label="City", initial="Windsor")
    province = forms.ChoiceField(required=True, choices=PROVINCE_CHOICES, label="Province")
    interested = forms.ModelMultipleChoiceField(required=True, queryset=Category.objects.all(),
                                                label="Interested Products", widget=forms.CheckboxSelectMultiple)
    photo = forms.ImageField(required=False, label="Profile Photo")

class Password_ResetForm(forms.Form):
    email = forms.EmailField(required=True, label="Email")
