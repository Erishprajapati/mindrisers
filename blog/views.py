from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .serializers import *
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib import messages
from django.contrib.auth import logout
from .forms import LoginForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User

# Create your views here.

def post_list(request):
    posts = Post.objects.all()  # Fetch all the posts
    paginator = Paginator(posts, 6)  # Create a paginator with 6 posts per page
    page_number = request.GET.get('page')  # Get the current page number from the request
    page_obj = paginator.get_page(page_number)  # Get the current page object
    
    # Pass both 'posts' and 'page_obj' in a single dictionary
    return render(request, 'post_list.html', {'posts': page_obj})

@login_required
def post_detail(request, post_slug):
    post = Post.objects.get(slug=post_slug)  # Use slug to get the post
    
    # Handle the comment submission
    if request.method == "POST":
        content = request.POST['content']
        
        # Ensure the comment is saved with the correct user and the post
        if request.user.is_authenticated:
            user = request.user._wrapped if hasattr(request.user, '_wrapped') else request.user
            comment = Comment(post=post, author=user, content=content)
            comment.save()
        else:
            # If the user is not authenticated, handle accordingly (e.g., show an error message)
            return redirect('login')  # Or another appropriate action if needed

        # Redirect to the same post page after adding the comment
        return redirect('post_detail', post_slug=post.slug)

    return render(request, 'post_detail.html', {'post': post})


@login_required
def create_post(request):
    categories = Category.objects.all()  # ✅ Fetch categories from the database

    if request.method == "POST":
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        content = request.POST.get('content')
        category_slug = request.POST.get('category')  # Fetching category by slug
        image = request.FILES.get('image')  # Handling file upload

        user = User.objects.get(username=request.user.username)  # ✅ Get actual User instance
        
        # ✅ Fetch category using slug instead of ID
        category = Category.objects.get(slug=category_slug)  

        Post.objects.create(
            title=title,
            slug=slug,
            content=content,
            category=category,  # ✅ Assign category using slug
            image=image,
            author=user  # ✅ Assign proper User instance
        )
        return redirect('home')

    return render(request, 'create_post.html', {'categories': categories})  # ✅ Pass categories

def search_blogs(request):
    query = request.GET.get('q')
    posts = Post.objects.filter(title__icontains=query)  # Corrected filter
    return render(request, 'search_results.html', {'posts': posts})

def filter_blogs(request, tag_name):
    posts = Post.objects.filter(tags__name=tag_name)  # Changed Blog to Post
    return render(request, 'filter_results.html', {'posts': posts})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        content = request.POST['content']
        Comment.objects.create(post=post, user=request.user, content=content)
    return redirect('post_detail', slug=post.slug)  # Fixed the redirect to use slug instead of id

# ViewSets for API
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
        post_id = self.request.query_params.get('post_id', None)
        if post_id:
            return Comment.objects.filter(post_id=post_id)
        return Comment.objects.all()

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        post_id = request.data.get('post_id')

        if not user_id or not post_id:
            return Response(
                {"message": "Both 'user_id' and 'post_id' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
            post = Post.objects.get(id=post_id)

            like, created = Like.objects.get_or_create(user=user, post=post)

            if not created:
                like.delete()
                return Response(
                    {"message": "Post Unliked"},
                    status=status.HTTP_200_OK
                )

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

def logout_confirmation(request):
    return render(request, 'logout.html')

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
        user = authenticate(request, username=username, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
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

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already in use")
            return redirect("register")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create the user's profile
        profile = Profile.objects.create(user=user, bio=bio)

        # Assign the profile picture if provided
        if profile_pic:
            profile.profile_picture = profile_pic
            profile.save()

        messages.success(request, "Registration successful! Please log in.")
        return redirect("login")

    return render(request, "register.html")
