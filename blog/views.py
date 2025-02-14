from django.shortcuts import render, get_object_or_404
from .models import Post

# Create your views here.
def post_list(request): #it shows the list of the post that can be viewed by the user
    posts = Post.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, slug): #it shows the detail of the post that can be viewed by the user
    post = get_object_or_404(Post, slug=slug) #slug shows the url instead of pk/id
    return render(request, 'blog/post_detail.html', {'post': post})

