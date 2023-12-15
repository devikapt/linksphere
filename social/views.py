from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.generic import FormView,CreateView,TemplateView,View,UpdateView,DetailView,ListView
from social.forms import RegistrationForm,LoginForm,UserProfileForm,PostForm,CommentForm
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from social.models import UserProfile,Posts
# Create your views here.

class SignUpView(CreateView):
    template_name="register.html"
    form_class=RegistrationForm

    def get_success_url(self):
        return reverse("signin")
    
class SignInView(FormView):
    template_name="login.html"
    form_class=LoginForm

    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request,username=uname,password=pwd)
            if user_object:
                login(request,user_object)
                print("login is successfully.......")
                return redirect("index")

            print("error in login")
            return redirect(request,"login.html",{"form":form})
        
class IndexView(CreateView,ListView):
    template_name="index.html"
    form_class=PostForm
    model=Posts
    context_object_name="data"
    


    def form_valid(self, form):
        form.instance.user=self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("index")

    def get_queryset(self):
        blocked_profile=self.request.user.profile.block.all()
        qs=Posts.objects.all().exclude(user__id__in=blocked_profile).order_by("-created_date")
        return qs
    

    
    

class SignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")
    
class ProfileUpdateView(UpdateView):
    template_name="profile_add.html"
    form_class=UserProfileForm
    model=UserProfile

    def get_success_url(self):
        return reverse("index")

class ProfileDetailView(DetailView):
    template_name="profile_detail.html"
    model=UserProfile
    context_object_name="data"

class ProfileListView(View):
    def get(self,request,*args,**kwargs):
        qs=UserProfile.objects.all().exclude(user=request.user)
        return render(request,"profile_list.html",{"data":qs})

class FollowView(View):
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        profile_object=UserProfile.objects.get(id=id)
        action=request.POST.get("action") #follow | unfollow
        if action=="follow":
            request.user.profile.following.add(profile_object)
        elif action=="unfollow":
         request.user.profile.following.remove(profile_object)


        return redirect("index")
    
# class PostListCreateView(CreateView):
#     template_name="index.html"
#     form_class=PostForm

#     def get_success_url(self):
#         return reverse("index")

class PostLikeView(View):
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        post_object=Posts.objects.get(id=id)
        action=request.POST.get("action")
        if action =="like":
            post_object.liked_by.add(request.user)
        elif action =="dislike":
            post_object.liked_by.remove(request.user)

        return redirect("index")
    
class CommentView(CreateView):
    template_name="index.html"
    form_class=CommentForm

    def get_success_url(self):
        return reverse("index")
    def form_valid(self,form):
        id=self.kwargs.get("pk")
        post_object=Posts.objects.get(id=id)
        form.instance.user=self.request.user
        form.instance.post=post_object
        return super().form_valid(form)
    
class ProfileBlockView(View):
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        profile_object=UserProfile.objects.get(id=id)
        action=request.POST.get("index")
        if action =="block":
            request.user.profile.block.add(profile_object)
        elif action =="unblock":
            request.user.profile.block.remove(profile_object)
        return redirect("index")