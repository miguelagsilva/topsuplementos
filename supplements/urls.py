from django.urls import path

from . import views

app_name = "supplements"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path('protein-powders/', views.protein_powders, name='protein_powders'),
]
