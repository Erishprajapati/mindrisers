from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
from .views import *



router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'likes', LikeViewSet, basename = 'like')

urlpatterns = [
    path('api/', include(router.urls)),
    path('',home,name='home'),
    path('create/', create_post, name="create_post"),
    path('post/<slug:post_slug>/', views.post_detail, name='post_detail'),
    
    path('post/<slug:slug>/', views.post_list, name='post_list'),
    path('login/', views.login_view, name = 'login'),
    path('register/', views.register_view, name = 'register'),
    path('logout/', logout_confirmation, name= 'logout'),
    path('confirm-logout', confirm_logout, name = 'confirm_logout'),
    path('saved/',saved_posts, name ='saved')
]

