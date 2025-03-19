from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def login_page(request):
    if request.user.is_authenticated:
        return redirect("/chat/riya")  

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect(request.GET.get("next", "/"))  # Redirects to 'next' URL if provided
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, "login.html")



@login_required
def logout_page(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect(request.GET.get("next", "/"))



def signup_view(request):
    if request.user.is_authenticated:
        return redirect("/chat/riya")  

    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        password1 = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Password Matching
        if password1 != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html")

        # Password Strength Check
        if len(password1) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, "signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "signup.html")

        if email and User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return render(request, "signup.html")

        user = User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, "Signup successful! Please log in.")
        return redirect("/login/")

    return render(request, "signup.html")
