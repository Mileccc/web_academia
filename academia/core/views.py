from typing import Any
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView
from django.contrib.auth.models import Group
from django.views import View
from django.utils.decorators import method_decorator

from .forms import RegisterForm, UserForm, ProfileForm
from .models import Course



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
        courses = Course.objects.all()
        
        context['courses'] = courses
        return context