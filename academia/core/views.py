import os
from typing import Any
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import Group, User
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin

from django.conf import settings

from .forms import RegisterForm, UserForm, ProfileForm, CourseForm
from .models import Course, Mark, Registration




def plural_to_singular(plural):
    plural_singular = {
        "estudiantes": "estudiante",
        "profesores":  "profesor",
        "preceptores": "preceptor",
        "administrativos": "administrativo"
    }
    
    return plural_singular.get(plural,"error")


# Crea un decorador personalizado
def add_group_name_to_context(view_class):
    """
    Este decorador agrega información del grupo del usuario al contexto de la vista.
    Permite a las vistas acceder a la información del grupo del usuario.
    """
    original_dispatch = view_class.dispatch
    
    
    def dispatch(self, request, *args, **kwargs):
        """
        Método que se ejecuta antes de llamar al método principal de la vista.
        Agrega información del grupo del usuario al contexto de la vista.
        """
        user = self.request.user
        group = user.groups.first()
        group_name = None
        group_name_singular = None
        color = None
        if group:
            if group.name == 'estudiantes':
                color = 'bg-primary'
            elif group.name == 'profesores':
                color = 'bg-success'
            elif group.name == 'preceptores':
                color = 'bg-secondary'
            elif group.name == 'administrativos':
                color = 'bg-danger'
                
            group_name = group.name
            group_name_singular = plural_to_singular(group.name)
            
        context = {
            'group_name': group_name,
            'group_name_singular': group_name_singular,
            'color': color
        }
        
        self.extra_context = context
        return original_dispatch(self, request, *args, **kwargs)

    view_class.dispatch = dispatch
    return view_class
    

# class CustomTemplateView(TemplateView):
#     group_name = None
#     group_name_singular = None
#     color = None
    
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = self.request.user
        
#         if user.is_authenticated:
#             group = Group.objects.filter(user=user).first()
#             if group:
#                 if group.name == 'estudiantes':
#                     self.color = 'bg-primary'
#                 elif group.name == 'profesores':
#                     self.color = 'bg-success'
#                 elif group.name == 'preceptores':
#                     self.color = 'bg-secondary'
#                 elif group.name == 'administrativos':
#                     self.color = 'bg-danger'
                    
#                 self.group_name = group.name
#                 self.group_name_singular = plural_to_singular(group.name)
#         context['group_name'] = self.group_name
#         context['group_name_singular'] = self.group_name_singular
#         context['color'] = self.color
#         return context

# PÁGINA DE PREGUNTAS Y RESPUESTAS  

# PÁGINA DE INICIO
@add_group_name_to_context
class HomeView(TemplateView):
    template_name = 'home.html'
       
       
# PAGINA DE PRECIOS
@add_group_name_to_context
class PricingView(TemplateView):
    template_name = 'pricing.html'
    
    
# REGISTRO DE USUARIOS
class RegisterView(View):
    def get(self, request):
        data = {
            'form': RegisterForm()
        }
        return render(request, 'registration/register.html', data)
    
    def post(self, request):
        user_creation_form = RegisterForm(data=request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()
            user = authenticate(username=user_creation_form.cleaned_data['username'], password=user_creation_form.cleaned_data['password1'])
            login(request, user)
            return redirect('home')
        
        data = {
            'form': user_creation_form
        }
        return render(request, 'registration/register.html', data)
    
# PÁGINA DE PERFIL
@add_group_name_to_context
class ProfileView(TemplateView):
    template_name = 'profile/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_form'] = UserForm(instance=user)
        context['profile_form'] = ProfileForm(instance=user.profile)
        
        if user.groups.first().name == 'profesores':
            # Obtener todos los cursos asignados al profesor
            assigned_courses = Course.objects.filter(teacher=user)
            context['assigned_courses'] = assigned_courses
        
        return context
    
    def post(self, request, *args, **kwargs):
        user = self.request.user
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # Redireccionar a la pagina de perfil (con datos actuializados)
            return redirect('profile')
        # Si alguno de los dos formularios no es valido
        context = self.get_context_data()
        context['user_form'] = user_form
        context['profile_form'] = profile_form
        return render(request, 'profile/profile.html', context)
        
# MOSTRAR TODOS LOS CURSOS
@add_group_name_to_context
class CoursesView(TemplateView):
    template_name = 'courses.html'
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        courses = Course.objects.all().order_by('-id')
        student = self.request.user if self.request.user.is_authenticated else None
        for item in courses:
            if student:
                registration = Registration.objects.filter(course=item, student=student).first()
                item.is_enrolled = registration is not None
            else:
                item.is_enrolled = False
            
            enrollment_count = Registration.objects.filter(course=item).count()
            item.enrollment_count = enrollment_count
        
        
        context['courses'] = courses
        return context

@add_group_name_to_context
class ErrorView(TemplateView):
    template_name = 'error.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error_image_path = os.path.join(settings.MEDIA_URL, 'error.png')
        context['error_image_path'] = error_image_path
        return context
    

  
# CREAR UN NUEVO CURSO
@add_group_name_to_context
class CourseCreateView(UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'create_course.html'
    success_url = reverse_lazy('courses')
    
    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists()
    
    def handle_no_permission(self):
        return redirect('error')
    
    def form_valid(self, form):
        messages.success(self.request, 'Curso creado con exito')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el curso')
        return self.render_to_response(self.get_context_data(form=form))
    

# EDITAR UN CURSO
@add_group_name_to_context
class CourseEditView(UserPassesTestMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'create_course.html'
    success_url = reverse_lazy('courses')
    
    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists()
    
    def handle_no_permission(self):
        return redirect('error')
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'El registro se ha actualizado satisfactoriamente')
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al actualizar el registro')
        return self.render_to_response(self.get_context_data(form=form))
    
    
@add_group_name_to_context
class CourseDeleteView(UserPassesTestMixin, DeleteView):
    model = Course
    template_name = 'delete_course.html'
    success_url = reverse_lazy('courses')
    
    def test_func(self):
        return self.request.user.groups.filter(name='administrativos').exists()
    
    def handle_no_permission(self):
        return redirect('error')
    
    def form_valid(self, form):
        messages.success(self.request, 'El registro se ha eliminado satisfactoriamente')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Ha ocurrido un error al eliminar el registro')
        
        
#   REGISTRO DE UN USUARIO EN UN CURSO
@add_group_name_to_context
class CoursEnrollmentView(TemplateView):
    def get(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)
        
        if request.user.is_authenticated and request.user.groups.first().name == 'estudiantes': 
            student = request.user
            
            # Crear un registro de inscripción asociado al estudiante y al curso
            registration = Registration.objects.create(student=student, course=course)
            registration.save()

            messages.success(request, 'Te has inscrito satisfactoriamente')
        else:
            messages.error(request, 'No se pudo completar la inscripción')
        
        return redirect('courses')

# MOSTRAR LISTA DE ALUMNOS Y NOTAS A LOS PROFESORES
@add_group_name_to_context
class StudentListMarkView(TemplateView):
    template_name = 'student_list_mark.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs['course_id']
        course = get_object_or_404(Course, pk=course_id)
        marks = Mark.objects.filter(course=course)
        
        student_data = []
        
        for mark in marks:
            student = get_object_or_404(User, pk=mark.student.id)
            student_data.append({
                'mark_id': mark.id,
                'name': student.get_full_name(),
                'mark_1': mark.mark_1,
                'mark_2': mark.mark_2,
                'mark_3': mark.mark_3,
                'average': mark.average
            })
        
        context['course'] = course
        
        context['student_data'] = student_data
        return context