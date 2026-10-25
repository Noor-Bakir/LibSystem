from django.db import models
from django.contrib.auth.models import User

# نموذج الكتاب
class Book(models.Model):
    title = models.CharField(max_length=200)        # عنوان الكتاب
    author = models.CharField(max_length=200)       # المؤلف
    isbn = models.CharField(max_length=13, unique=True)  # رقم الكتاب
    quantity = models.IntegerField(default=1)        # عدد النسخ
    available = models.BooleanField(default=True)    # متوفر أم لا

    def __str__(self):
        return self.title

# نموذج الاستعارة
class Borrowing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)   # تاريخ الاستعارة
    return_date = models.DateField(null=True, blank=True) # تاريخ الإرجاع
    returned = models.BooleanField(default=False)         # هل أُرجع؟

    def __str__(self):
        return f"{self.user} - {self.book}"