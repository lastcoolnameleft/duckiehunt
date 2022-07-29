""" Duck URL router """
from django.conf.urls import include
from django.urls import path

from . import views, apis

urlpatterns = [
    # ex: /
    path('', views.index, name='index'),
    path('duck/', views.duck_list, name='duck_list'),
    path('faq/', views.faq, name='faq'),
    path('issue/', views.issue, name='issue'),
    path('privacy/', views.privacy, name='privacy'),
    path('tos/', views.tos, name='tos'),
    path('mark/', views.mark, name='mark'),
    # ex: /view/duck/5/
    path('view/duck/<int:duck_id>', views.detail, name='duck_list'),
    path('duck/<int:duck_id>', views.detail, name='detail'),
    # ex: /view/location/500/
    path('view/location/<int:duck_location_id>', views.location, name='location'),
    path('location/<int:duck_location_id>', views.location, name='location'),
    # APIs
    path('api/duck/<int:duck_id>', apis.detail, name='detail'),
    # Auth
    path('profile', views.profile, name='profile'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('oauth/', include('social_django.urls', namespace='social'), name='logthru'),
]
