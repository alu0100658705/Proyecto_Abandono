from django import forms
from allauth.account.forms import LoginForm
from allauth.account.forms import SignupForm
"""
class MyLoginForm(LoginForm):
    def login(self, *args, **kwargs):
        self.fields['login'] = forms.EmailField(label='E-mail')
        self.fields['login'].widget.attrs["placeholder"] = "E-mail"
        self.fields['password'] = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
        self.fields['password'].widget.attrs["placeholder"] = "Contraseña"
        return super(MyLoginForm, self).login(*args, **kwargs)

class MySignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(MySignupForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(label="Nombre")
        self.fields['name'].widget.attrs["placeholder"] = "Nombre"
    def save(self, request):
        user = super(MySignupForm, self).save(request)
        return user
"""

class VarForm(forms.Form):
    def __init__(self, *args, **kwargs):
        my_vars = kwargs.pop('custom_variables', None) 
        super(VarForm, self).__init__(*args, **kwargs)
        self.fields['variables'] = forms.ChoiceField(
            choices=[(var, var) for var in my_vars]
        )