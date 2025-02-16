from django.db import models
from django.utils.text import slugify
# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=30)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null = True, blank = True)
    bio = models.CharField(max_length=100, blank = True)
    created_at = models.DateTimeField(auto_created=True)

    def __str__(self):
        return self.username
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Auto-generate slug from name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="posts", null=True, blank=True)  # Add this line
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image_url = models.URLField(blank=True, null=True)  # Ensure this field exists
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)  # Automatically generate a slug from the title
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)  # Add related_name='comments'
    author = models.ForeignKey(User, on_delete=models.CASCADE) 
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Fix auto_created issue

    def __str__(self):
        return self.author.username

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_created=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = "profile")
    bio = models.TextField()
    profile_picture = models.ImageField(upload_to = 'profile_pics/', blank = True, null = True)

    def __str__(self):
        return self.user.username