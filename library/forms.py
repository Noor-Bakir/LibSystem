from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'quantity', 'available']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان الكتاب'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المؤلف'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم ISBN'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }