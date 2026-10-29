from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Book, Borrowing
from .forms import BookForm


# السماح للموظفين (المسؤولين) فقط
staff_required = user_passes_test(lambda u: u.is_active and u.is_staff, login_url='/login/')


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
    query = request.GET.get('q', '').strip()
    books = Book.objects.none()
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
    return render(request, 'library/book_search.html', {'books': books, 'query': query})


@staff_required
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


@staff_required
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


@staff_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'تم حذف الكتاب بنجاح ✅')
        return redirect('book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})


# تسجيل الدخول
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
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
    with transaction.atomic():
        book = get_object_or_404(Book.objects.select_for_update(), pk=pk)

        if Borrowing.objects.filter(user=request.user, book=book, returned=False).exists():
            messages.warning(request, 'لقد استعرت هذا الكتاب بالفعل.')
        elif book.available and book.quantity > 0:
            Borrowing.objects.create(user=request.user, book=book)
            book.quantity -= 1
            book.available = book.quantity > 0
            book.save()
            messages.success(request, 'تمت الاستعارة بنجاح ✅')
        else:
            messages.error(request, 'الكتاب غير متوفر حالياً.')

    return redirect('book_detail', pk=pk)


# إرجاع كتاب
@login_required
def return_book(request, pk):
    with transaction.atomic():
        borrowing = get_object_or_404(
            Borrowing.objects.select_for_update(), pk=pk, user=request.user
        )
        if borrowing.returned:
            messages.info(request, 'تم إرجاع هذا الكتاب مسبقاً.')
        else:
            borrowing.returned = True
            borrowing.return_date = timezone.localdate()
            borrowing.save()

            book = borrowing.book
            book.quantity += 1
            book.available = True
            book.save()
            messages.success(request, 'تم إرجاع الكتاب ✅')
    return redirect('my_books')


# كتب المستخدم المستعارة
@login_required
def my_books(request):
    borrowings = Borrowing.objects.filter(
        user=request.user, returned=False
    ).select_related('book')
    return render(request, 'library/my_books.html', {'borrowings': borrowings})


# لوحة التحكم
@staff_required
def dashboard(request):
    context = {
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(available=True, quantity__gt=0).count(),
        'borrowed_books': Borrowing.objects.filter(returned=False).count(),
        'total_borrowings': Borrowing.objects.count(),
        'recent_borrowings': Borrowing.objects.select_related('book', 'user')
                                              .order_by('-borrow_date', '-pk')[:20],
    }
    return render(request, 'library/dashboard.html', context)


# حذف سجل استعارة (للمسؤول، للسجلات المُرجعة فقط)
@staff_required
def borrowing_delete(request, pk):
    borrowing = get_object_or_404(Borrowing, pk=pk)

    if not borrowing.returned:
        messages.error(request, 'لا يمكن حذف سجل لم يُرجع كتابه بعد.')
        return redirect('dashboard')

    if request.method == 'POST':
        borrowing.delete()
        messages.success(request, 'تم حذف سجل الاستعارة ✅')
        return redirect('dashboard')

    return render(request, 'library/borrowing_confirm_delete.html', {'borrowing': borrowing})
