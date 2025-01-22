from allauth.account.forms import SignupForm
from apps.accounts.models import UserAccount
from django import forms

class CustomSignupForm(SignupForm):
    email = forms.EmailField(max_length=255, label="Email")
    full_name = forms.CharField(max_length=30, label="First Name")
    profile_image = forms.ImageField(required=False, label="Profile Image")
    phone = forms.CharField(max_length=20, required=False, label="Phone Number")
    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        password = self.cleaned_data['password1']
        user.set_password(password)
        user.full_name = self.cleaned_data['full_name']
        user.phone = self.cleaned_data['phone']
        user.save()
        return user

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = ['full_name',  'profile_image', 'phone', 'branch']

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)