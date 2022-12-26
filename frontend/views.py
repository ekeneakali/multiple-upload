from django.shortcuts import render, redirect

from django.contrib.auth.models import User

from . forms import *

from frontend.models import *

from django.contrib import messages

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

from .tokens import account_activation_token
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
import os
from .forms import SetPasswordForm
from .forms import PasswordResetForm

 
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import  ListView
from hitcount.views import HitCountDetailView
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountMixin
from django.urls import reverse_lazy
from django.http.response import JsonResponse
from cart.cart import Cart




# from django.contrib.auth.forms import authenticate, login



# Create your views here.


def home(request):
    post = Product.objects.all()

    return render(request, 'frontend/home.html', {'post':post, 'post':post})
def base(request):

    post = Cart.objects.all()

    return render(request, 'frontend/base.html', {'post':post})   
   
def two(request, pst):
    race = Product.objects.get(pk=pst)
    related = Product.objects.filter(name=race)
    if race:
        race.views = race.views +1
    is_liked = False
    is_favourite = False
    if race.likes.filter(id=request.user.id).exists():
        is_liked = True
    
    if race.favourite.filter(id=request.user.id).exists():
        is_favourite = True


    return render(request, 'frontend/two.html', {'race':race, 'related':related, 'is_liked':is_liked, 'total_likes':race.total_likes, 'is_favourite':is_favourite})

def like_post(request, pk):
    post = get_object_or_404(Product, id=request.POST.get('post_id'))
    is_liked = False
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:

        post.likes.add(request.user)
        is_liked = True
            
    return HttpResponseRedirect(reverse('frontend:two', args=[str(pk)]))

def view_post(request):

    post = Product.objects.filter(name=request.user)


    return render(request, 'frontend/view_post.html', {'post':post})
  

def info(request):
    if request.method == 'POST':
        form = Info(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            messages.success(request, 'thanks for the data')
            return redirect('frontend:info')
            
    else:
        form = Info()

        return render(request, 'frontend/info.html', {'form':form})

    

    
    

def one(request, pst):
    race = Document.objects.get(pk=pst)

    return render(request, 'frontend/one.html', {'race':race})
    hit_count = True





def register(request):
    if request.method == "POST":
        form = Register(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('frontend:register')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = Register()

    return render(request, "frontend/register.html", {"form": form}
        )
        


def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('frontend/account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on \
            received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')
def activate(request, uidb64, token):
    user = User()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('frontend:custom_login')
    else:
        messages.error(request, 'Activation link is invalid!')
    
    return redirect('home')

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Hello <b>{user.username}</b>! You have been logged in")
                return redirect('home')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error) 

    form = AuthenticationForm() 
    
    return render(request, "frontend/login.html", {'form': form}
        )
# Same as in all places where we request some input from the user, we use the POST method; not an exception is the login function. We use the built-in Django Authentication form to receive the username and password from the user and check if it's valid. If the form is valid, we call the built-in Django authentication function that checks if such a 

def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("frontend:custom_login")

def confirm_logout(request):

    return render(request, 'frontend/confirm-logout.html')

def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('frontend:custom_login')

    if request.method == 'POST':
        form = EditProfile(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'profile edited successfully')
        else:
            messages.error(request, 'user not edited')
    else:
        form = Register(instance=request.user)


    return render(request, 'frontend/edit-profile.html', {'form':form})


def password_change(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")
            return redirect('frontend:custom_login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return render(request, 'frontend/password_reset_confirm.html', {'form': form})

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = User.objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("frontend/reset.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                        """
                        <h2>Password reset sent</h2><hr>
                        <p>
                            We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                            You should receive them shortly.<br>If you don't receive an email, please make sure you've entered the address 
                            you registered with, and check your spam folder.
                        </p>
                        """
                    )
                else:
                    messages.error(request, "Problem sending reset password email, <b>SERVER PROBLEM</b>")

            return redirect('home')

        for key, error in list(form.errors.items()):
            if key == 'captcha' and error[0] == 'This field is required.':
                messages.error(request, "You must pass the reCAPTCHA test")
                continue

    form = PasswordResetForm()
    return render(request, "frontend/password_reset.html", {"form": form}
        )
def passwordResetConfirm(request, uidb64, token):
    user = User()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in </b> now.")
                return redirect('frontend:custom_login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render(request, 'frontend/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("home")


def news(request):
    if request.method == "POST":
        form = NewsLetterForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            send_mail(
            name,
            email,
            'akaliekene42@gmail.com',
            ['waltrade42@gmail.com'],
            fail_silently=False,
            
        )

            messages.success(request, 'thanks for subscribing')
            return redirect('frontend:news')

    else:
        form = NewsLetterForm()

    return render(request, "frontend/subscribe.html", {"form": form}
        )


def BlogPostLike(request, pk):
    post = get_object_or_404(BlogPost, id=request.POST.get('blogpost_id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return HttpResponseRedirect(reverse('blogpost-detail', args=[str(pk)]))


def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    messages.success(request, 'product added to cart successfully')
    return HttpResponseRedirect(reverse('frontend:two', args=[str(id)]))

def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("frontend:cart_detail")



def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("frontend:cart_detail")

def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("frontend:cart_detail")

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("frontend:cart_detail")

def cart_detail(request):

    return render(request, 'frontend/cart_detail.html')

def checkout(request):

    return render(request, 'frontend/checkout.html')



def favourite_post(request, id):

    post = Product.objects.get(id=id)

    if post.favourite.filter(id=request.user.id).exists():
        post.favourite.remove(request.user)
        messages.success(request, 'product added to whishlist')

    else:
        post.favourite.add(request.user)
        messages.info(request, 'product remove from whishlist')


    return HttpResponseRedirect(reverse('frontend:two', args=[str(id)]))

def post_list(request):

    user = request.user

    favourite_post = user.favourite.all()

    return render(request, 'frontend/post_list_favourite.html', {'favourite_post':favourite_post})

def error_404_view(request, exception):

    return render(request, 'frontend/404.html')
