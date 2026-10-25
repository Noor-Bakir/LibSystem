from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Borrowing
from .forms import BookForm
from django.contrib import messages
# الصفحة الرئيسية - عرض كل الكتب
def book_list(request):
    books = Book.objects.all()
    return render(request, 'library/book_list.html', {'books': books})

# صفحة تفاصيل كتاب معين
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'library/book_detail.html', {'book': book})

# صفحة البحث عن كتاب
def book_search(request):
    query = request.GET.get('q', '')
    books = Book.objects.filter(title__icontains=query) | Book.objects.filter(author__icontains=query)
    return render(request, 'library/book_search.html', {'books': books, 'query': query})

def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تمت إضافة الكتاب بنجاح ✅')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form, 'title': 'إضافة كتاب'})

def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الكتاب بنجاح ✅')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form, 'title': 'تعديل كتاب'})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'تم حذف الكتاب بنجاح ✅')
        return redirect('book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

# تسجيل الدخول
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('book_list')
    else:
        form = AuthenticationForm()
    return render(request, 'library/login.html', {'form': form})

# تسجيل الخروج
def user_logout(request):
    logout(request)
    return redirect('book_list')

# إنشاء حساب جديد
def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('book_list')
    else:
        form = UserCreationForm()
    return render(request, 'library/register.html', {'form': form})

# استعارة كتاب
@login_required
def borrow_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.available:
        Borrowing.objects.create(user=request.user, book=book)
        book.available = False
        book.save()
    return redirect('book_detail', pk=pk)

# إرجاع كتاب
@login_required
def return_book(request, pk):
    borrowing = get_object_or_404(Borrowing, pk=pk, user=request.user)
    borrowing.returned = True
    borrowing.return_date = borrowing.borrow_date
    borrowing.save()
    borrowing.book.available = True
    borrowing.book.save()
    return redirect('my_books')

# كتب المستخدم المستعارة
@login_required
def my_books(request):
    borrowings = Borrowing.objects.filter(user=request.user, returned=False)
    return render(request, 'library/my_books.html', {'borrowings': borrowings})

from django.contrib.auth.decorators import login_required
from django.db.models import Count

# لوحة التحكم
def dashboard(request):
    total_books = Book.objects.count()
    available_books = Book.objects.filter(available=True).count()
    borrowed_books = Book.objects.filter(available=False).count()
    total_borrowings = Borrowing.objects.count()
    recent_borrowings = Borrowing.objects.order_by('-borrow_date')[:5]
    
    context = {
        'total_books': total_books,
        'available_books': available_books,
        'borrowed_books': borrowed_books,
        'total_borrowings': total_borrowings,
        'recent_borrowings': recent_borrowings,
    }
    return render(request, 'library/dashboard.html', context)