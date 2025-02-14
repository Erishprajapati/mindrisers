from django.shortcuts import render, get_object_or_404
from .models import *
from .serializers import *
from rest_framework import viewsets, status
from rest_framework.response import Response

# Create your views here.
def post_list(request): #it shows the list of the post that can be viewed by the user
    posts = Post.objects.all()
    return render(request, 'post_list.html', {'posts': posts})

def post_detail(request, slug): #it shows the detail of the post that can be viewed by the user
    post = get_object_or_404(Post, slug=slug) #slug shows the url instead of pk/id
    return render(request, 'blog/post_detail.html', {'post': post})

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