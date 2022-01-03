from django.urls import path
from . import views

app_name='ledger'
urlpatterns = [
    path('', views.index, name='index'),
    path('show_off/', views.show_off, name='show_off'),
    path('show_off/<int:off_id>/', views.show_off, name='show_off'),
    path('create_acc/', views.create_acc, name='create_acc'),
    path('<int:acc_id>/create-trans/<trans_type>', views.create_trans, name='create_trans'),
    path('<int:acc_id>/show-acc/', views.show_acc, name='show_acc'),
    path('<int:trans_id>/voucher/', views.voucher, name='voucher'),
    path('<int:trans_id>/receipt/', views.receipt, name='receipt'),
    path('create-cli-acc/', views.create_cli_acc, name='create_cli_acc'),
    path('create-off-acc/', views.create_off_acc, name='create_off_acc'),
    path('add-type-codes/', views.create_tc, name='create_tc'),
    path('<int:tc_id>/remove-tc/', views.remove_tc, name='remove_tc'),
    path('show-client-accounts/', views.show_cli, name='show_cli'),
    path('search-results/', views.search, name='search'),
    path('<int:acc_id>/create_ad/', views.create_ad, name='create_ad'),
    path('<int:acc_id>/tax/', views.tax, name='tax'),
    path('total_tax/', views.total_tax, name='total_tax'),
    path('adat-index/', views.adat_index, name="adat_index"),
    path('<int:trans_id>/resolve-adat/', views.resolve, name='resolve'),
    path('<int:acc_id>/custom-receipt/', views.custom_receipt, name='custom_receipt'),
    path('uncleared-credits/', views.uncleared, name='uncleared'),
    path('counter_trans/', views.counter_trans, name='counter_trans'),
    path('<int:acc_id>/subj_matter/', views.subj_matter, name='subj_matter'),
    path('<int:acc_id>/edit-info/', views.edit_info, name='edit_info')
]