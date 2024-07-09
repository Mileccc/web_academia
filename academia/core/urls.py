from django.urls import path
from .views import ErrorView, HomeView, PricingView, RegisterView, ProfileView, CoursesView, CourseCreateView, CourseEditView,CourseDeleteView,CoursEnrollmentView, StudentListMarkView, UpdateMarkView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # PÁGINA DE INICIO
    path('', HomeView.as_view(), name="home"),
    # PÄGINA DE PRECIOS
    path('pricing/', PricingView.as_view(), name="pricing"),
    # PAGINA DE LOGIN y REGISTRO
    path('register/', RegisterView.as_view(), name="register"),
    # PÁGINAS DE PERFIL: VISTA DE PERFIL - EDICIÓN DEL PERFIL
    path('profile/', login_required(ProfileView.as_view()), name="profile"),
    # PÁGINA QUE ADMINISTRA LOS CURSOS: LISTA DE CURSOS - ( CREACIÓN - EDICIÓN - ELIMINAR )
    path('courses/', CoursesView.as_view(), name="courses"),  
    path('courses/create/', login_required(CourseCreateView.as_view()), name="course_create"),
    path('error/', login_required(ErrorView.as_view()), name="error"),
    path('courses/<int:pk>/edit/', login_required(CourseEditView.as_view()), name="course_edit"),
    path("courses/<int:pk>/delete/", login_required(CourseDeleteView.as_view()), name="course_delete"),
    # INSCRIPCIÓN DE UN ALUMNO EN UN CURSO
    path("enroll_course/<int:course_id>/", login_required(CoursEnrollmentView.as_view()), name="enroll_course"),
    # PROFESOR AÑADIR NOTAS
    path("courses/<int:course_id>", login_required(StudentListMarkView.as_view()), name="student_list_mark"),
    path('courses/update_mark/<int:mark_id>/', login_required(UpdateMarkView.as_view()), name="update_mark"),
    
    
]
