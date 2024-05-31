from django.urls import path, include
from rest_framework import routers
from api import views

# Importa la vista LoginView desde api/views.py
#from .views import LoginView


router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'result', views.RegistroViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/login/', views.LoginView.as_view(), name='login'),
    path('users/results/<int:id_user>/', views.RegistroViewSet.ResultUser.as_view(), name='results'),  # Ruta para obtener resultados
    path('users/inference/', views.InferenceView.as_view(), name='inference'), 
    path('email/', views.ReportView.as_view(), name='email') 
]
