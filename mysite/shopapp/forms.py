from django import forms
from .models import Product, Order
from django.contrib.auth.models import Group


class GroupForm(forms.ModelForm):
    
    class Meta:
        model = Group
        fields = ["name",]


class ProductForm(forms.ModelForm):

    # поля формы описаны с целью настройки проверок валидности заполнения
    # (ограничения отличаются от указанных в модели)
    name = forms.CharField(label="Название продукта", max_length=100, min_length=3)
    price = forms.DecimalField(label="Цена",min_value=150, max_value=20000, decimal_places=2)
    discount = forms.IntegerField(label="Скидка", initial=0, min_value=0, max_value=50)
    images = forms.ImageField(widget=forms.ClearableFileInput())
      
    class Meta:
        model = Product
        fields = ["name", "description", "price", "discount", "images"]
        widgets = {
            "description": forms.Textarea(attrs={"rows":5, "max_cols":50,
                                                 "required":"True", "maxlength":1000}),
        }
    
class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ["user","products", "promocode", "delivery_address"]
        widgets = {
            "delivery_address": forms.Textarea(attrs={"rows":5, "max_cols":50,
                                                      "required":"True", "maxlength":200}),
        }


class CSVImportForm(forms.Form):

    csv_file = forms.FileField()


class CSVImportManyForm(forms.Form):

    csv_file = forms.FileField()
    # csv_related_file = forms.FileField()
