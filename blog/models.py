from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import *
from django.conf import settings 
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
    slug = models.SlugField(unique=True, blank=True, null=True, default = "")
    description = models.TextField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  # Auto-generate slug from name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name #returns a readable name instead of complex object type
    
class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="posts", null=True, blank=True)  # Add this line
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image_url =models.ImageField(upload_to='post_images/', null=True, blank=True)  # Stores images in "media/profile-picture"
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
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_created=True)

class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Reference the custom user model
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username

    def __str__(self):
        return self.user.username  # Update this line as well

    def __str__(self):
        return self.User.username
    
class SavedPost(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user} saved {self.post}"

# class UserAction(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models)
#     liked = models.BooleanField(default=False)
#     saved = models.BooleanField(default=False)

class CustomUserManager(BaseUserManager):  # ✅ Inherit from BaseUserManager
    def create_user(self, email, username, password=None, **extra_fields):
        
        if not username:
            raise ValueError("The Username field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # ✅ Set the password properly
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        # extra_fields.setdefault('is_staff', True)
        # extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)  

    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # ✅ 'user' is not a valid field, replaced with 'username'

    def __str__(self):
        return self.email