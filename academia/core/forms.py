from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from accounts.models import Profile

class LoginForm(AuthenticationForm):
    pass
    
    
class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(label='Nombre')
    last_name = forms.CharField(label='Apellidos')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        
    def clean_email(self):
        email_field = self.cleaned_data['email']
        if User.objects.filter(email=email_field).exists():
            raise forms.ValidationError('El correo electrónico ya existe')
        return email_field
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model  = Profile
        fields  = ['image', 'address', 'location', 'telephone']
        
