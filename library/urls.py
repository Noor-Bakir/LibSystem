from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('search/', views.book_search, name='book_search'),
    path('book/add/', views.book_add, name='book_add'),
    path('book/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('book/<int:pk>/borrow/', views.borrow_book, name='borrow_book'),
    path('borrowing/<int:pk>/return/', views.return_book, name='return_book'),
    path('my-books/', views.my_books, name='my_books'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
