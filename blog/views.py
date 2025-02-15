from django.shortcuts import render, get_object_or_404,redirect
from .models import *
from .serializers import *
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib import messages
from django.contrib.auth import logout
from .forms import LoginForm
from django.contrib.auth import authenticate, login

# Create your views here.
def post_list(request): #it shows the list of the post that can be viewed by the user
    posts = Post.objects.all()
    return render(request, 'post_list.html', {'posts': posts})

def post_detail(request, slug): #it shows the detail of the post that can be viewed by the user
    post = get_object_or_404(Post, slug=slug) #slug shows the url instead of pk/id
    return render(request, 'post_detail.html', {'post': post})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.request.query_params.get('post_id', None)  # Fixed typo
        if post_id:
            return Comment.objects.filter(post_id=post_id)
        return Comment.objects.all()

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        post_id = request.data.get('post_id')

        # Check if user_id and post_id are provided
        if not user_id or not post_id:
            return Response(
                {"message": "Both 'user_id' and 'post_id' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
            post = Post.objects.get(id=post_id)

            # Check if like already exists for the given user and post
            like, created = Like.objects.get_or_create(user=user, post=post)

            if not created:
                like.delete()  # Remove the like if it already exists (unlike the post)
                return Response(
                    {"message": "Post Unliked"},
                    status=status.HTTP_200_OK
                )

            # Create a new like if it didn't exist
            return Response(
                {"message": "Post Liked"},
                status=status.HTTP_201_CREATED
            )

        except User.DoesNotExist:
            return Response(
                {"message": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Post.DoesNotExist:
            return Response(
                {"message": "Post not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
def home(request):
    posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts})

def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')


def logout_confirmation(request):
    """Render the logout confirmation page."""
    return render(request,'logout.html')


def confirm_logout(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "Account logout successfully")
        return redirect('home')
    return redirect('logout')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=username, email = email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home after successful login
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        bio = request.POST['bio']
        profile_pic = request.FILES.get('profile_pic')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already in use")
            return redirect("register")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        # Creating a new user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Save additional details (assuming Profile model exists)
        user.profile.bio = bio  # Profile model should have a OneToOneField linked to User
        if profile_pic:
            user.profile.profile_picture = profile_pic  # Assuming Profile model has `profile_picture`
        user.profile.save()  # Save profile

        messages.success(request, "Registration successful! Please log in.")
        return redirect("login")

    return render(request, "register.html")
