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
# from django.contrib.auth.models import User
# from django.http import JsonResponse
# from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from django.contrib.auth import get_user_model


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
    post = get_object_or_404(Post, slug=post_slug)  # Get the post by slug
    
    # Handle the comment submission
    if request.method == "POST":
        content = request.POST['content']
        
        if request.user.is_authenticated:
            comment = Comment(post=post, author=request.user, content=content)
            comment.save()
        else:
            # If user is not authenticated, redirect or show error
            return redirect('login')  # Redirect to login page (adjust URL if needed)

        # After saving the comment, redirect to the same post page
        return redirect('post_detail', post_slug=post.slug)

    return render(request, 'post_detail.html', {'post': post})

# def update_like(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         liked = data.get('liked', False)
#         post_slug = data.get('post_slug', None)

#         if post_slug:
#             post = Post.objects.get(slug = post_slug)
#             user_action, created = UserAction.objects.get_or_create(user = request.user, post = post)
#             user_action.liked = liked
#             user_action.save()
#             return JsonResponse({'status': 'success', 'liked': liked})

#     return JsonResponse({'status': 'error'}, status=400)

@login_required
def create_post(request):
    categories = Category.objects.all()
    User = get_user_model()  # ✅ Get the User model

    if request.method == "POST":
        title = request.POST.get('title')
        slug = request.POST.get('slug')
        content = request.POST.get('content')
        category_slug = request.POST.get('category')  # ✅ Slug for category
        image = request.FILES.get('image')

        # ✅ Convert Lazy User Object to actual User instance
        author = request.user

        # ✅ Fetch category safely
        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            messages.error(request, "Invalid category selected.")
            return redirect('create_post')

        # ✅ Correctly assign the author instance
        Post.objects.create(
            title=title,
            slug=slug,
            content=content,
            category=category,
            image=image,
            author= CustomUser
        )
        # Post.save() 
        
        return redirect('home')

    return render(request, 'create_post.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)  # Fetch single category
    categories = Category.objects.all()  # Fetch all categories for the navbar
    return render(request, 'category_detail.html', {'category': category, 'categories': categories})

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

# def CategoryDetailview(request):
#     categories = Category.objects.all()
#     return render(request, "base.html", {"categories": categories})

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
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        bio = request.POST.get("bio")
        profile_pic = request.FILES.get("profile_pic")

        # Check if username or email already exists
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username is already in use")
            return redirect("register")
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        # Create the user
        user = CustomUser.objects.create_user(username=username, email=email, password=password)

        # Create the profile
        profile = Profile.objects.create(user=CustomUser, bio=bio)  # Use 'user=user'

        if profile_pic:
            profile.profile_picture = profile_pic
            profile.save()

        login(request, user)

        messages.success(request, "Registration successful! You are now logged in.")
        return redirect("home")

    return render(request, "register.html")


@login_required
def saved_posts(request):
    try:
        user = User.objects.get(username=request.user.username)  # Ensure it's a User instance
        saved_posts = SavedPost.objects.filter(user=request.user)
        # user = user.save()
        return render(request, 'saved.html', {'saved_posts': saved_posts})
    except User.DoesNotExist:
        return render(request, 'saved.html', {'error': 'User not found'})

# def Category_detail(request, slug):
#     category = get_object_or_404(Category, slug=slug)  # Use lowercase variable name
#     posts = category.posts.all()  # Fetch posts related to the category

#     return render(request, 'category_detail.html', {'category': category, 'posts': posts})


@login_required
def like_post(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug)
    
    # Check if the user already liked the post
    existing_like = Like.objects.filter(user=request.user, post=post).first()

    
    if existing_like:
        # If the like exists, remove it (unlike)
        existing_like.delete()
    else:
        # If the like doesn't exist, create a new like
        Like.objects.create(username=request.user, post=post)

    return redirect('post_detail', post_slug=post.slug)

