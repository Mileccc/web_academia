from django.urls import path
from .views import HomeView, PricingView, RegisterView, ProfileView, CoursesView

urlpatterns = [
    # PÁGINA DE INICIO
    path('', HomeView.as_view(), name="home"),
    # PÄGINA DE PRECIOS
    path('pricing/', PricingView.as_view(), name="pricing"),
    # PAGINA DE LOGIN y REGISTRO
    path('register/', RegisterView.as_view(), name="register"),
    # PÁGINAS DE PERFIL: VISTA DE PERFIL - EDICIÓN DEL PERFIL
    path('profile/', ProfileView.as_view(), name="profile"),
    # PÁGINA QUE ADMINISTRA LOS CURSOS: LISTA DE CURSOS - ( CREACIÓN - EDICIÓN - ELIMINAR )
    path('courses/', CoursesView.as_view(), name="courses"),  
]
