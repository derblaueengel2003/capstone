from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50) # Required
    last_name = forms.CharField(max_length=50) # Required
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username", "password1", "password2")
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('index')
        else:
            # Return an 'invalid login' error message.
            messages.success(request, ("There was an error logging in, try again..."))
            return redirect('login')

    else:
        return render(request, 'authenticate/login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("Successfully logged out."))
    return redirect('index')

def register_user(request):

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request,("Registration successfull"))

            return redirect('index')
    else:
        form = SignUpForm()


    return render(request, "authenticate/register_user.html", {
        'form': form
    })

def edit_user(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        # profile_form = ProfileForm(request.POST, instance=request.user.profile)
        # if user_form.is_valid() and profile_form.is_valid():
        if user_form.is_valid():
            user_form.save()
            # profile_form.save()
            messages.success(request, ('Your profile was successfully updated!'))
            
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        # profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'authenticate/profile.html', {
        'user_form': user_form,
        # 'profile_form': profile_form
    })