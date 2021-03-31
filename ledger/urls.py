from django.urls import path
from . import views

app_name='ledger'
urlpatterns = [
    path('', views.index, name='index'),
    path('show_off/', views.show_off, name='show_off'),
    path('create_acc/', views.create_acc, name='create_acc'),
    path('<int:acc_id>/create-trans/', views.create_trans, name='create_trans'),
    path('<int:acc_id>/show-acc/', views.show_acc, name='show_acc'),
    path('<int:trans_id>/voucher/', views.voucher, name='voucher'),
    path('<int:trans_id>/receipt/', views.receipt, name='receipt')
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]