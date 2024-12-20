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
    path('mark/<int:duck_id>', views.mark, name='mark'),
    path('mark_captcha/', views.mark_captcha, name='mark_captcha'),
    path('mark_captcha/<int:duck_id>', views.mark_captcha, name='mark_captcha'),
    # ex: /view/duck/5/
    path('view/duck/<int:duck_id>', views.detail, name='duck_list'),
    path('duck/<int:duck_id>', views.detail, name='detail'),
    path('found/<int:duck_id>', views.found, name='found'),
    # ex: /view/location/500/
    path('view/location/<int:duck_location_id>', views.location, name='location'),
    path('location/<int:duck_location_id>', views.location, name='location'),
    # APIs
    path('api/duck/<int:duck_id>', apis.duck_detail, name='detail'),
    path('api/ducks', apis.ducks_all),
    path('api/locations', apis.locations_all),
    path('api/duck/<int:duck_id>/locations', apis.duck_locations),
    path('api/duck/<int:duck_id>/', apis.duck_locations),
    path('api/location/<int:duck_location_id>', apis.location),
    # Auth
    path('profile', views.profile, name='profile'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('oauth/', include('social_django.urls', namespace='social'), name='logthru'),
]
