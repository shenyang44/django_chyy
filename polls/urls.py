from django.urls import path
from . import views

app_name='polls'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('create_acc/', views.create_acc, name='create_acc'),
    path('<int:acc_id>/create_trans/', views.create_trans, name='create_trans')
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]