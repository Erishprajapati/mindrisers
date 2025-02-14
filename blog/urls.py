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
    path('login/', views.login_view, name = 'login'),
    path('register/', views.register_view, name = 'register')
]
