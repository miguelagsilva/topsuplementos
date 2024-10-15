from django.urls import path

from . import views

app_name = "supplements"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path('protein-powders/', views.protein_powders, name='protein_powders'),
    path('protein-powders/<str:protein_type>/', views.protein_powders, name='protein_powders_by_type'),
    path('creatines/', views.creatines, name='creatines'),
    path('creatines/<str:creatine_form>/<str:creatine_type>/', views.creatines, name='creatines_by_type'),
]
