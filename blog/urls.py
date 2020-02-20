from django.urls import path, include
from . import views
from register import views as v

urlpatterns = [
    # path('', views.home, name='blog-home'),
    path('', views.index, name='blog-home'),
    path('home/', views.index, name='blog-home'),
    path('about/', views.about, name='blog-about'),
    path('macie/', views.macie, name='blog-macie'),
    path('macie_reviewed/', views.macie_reviewed),
    path('macie_downloaded/', views.macie_downloaded),
    path('upload', views.upload_index, name='blog-upload'),
    path('submit/upload', views.upload_index, name='blog-upload'),
    path('upload/complete', views.upload_complete),
    path('submit/upload/complete', views.upload_complete),
    path('submit/', views.submit, name='blog-test'),
    path('register/', v.register),
    path('submit/submit_success/', views.submit_success, name='blog-submit-success'),
    path('', include("django.contrib.auth.urls")),
    path('videoplayer/', views.videoplayer, name='blog-videoplayer'),
    path('update_macie/', views.update_macie_twitch),
    path('update_macie_daily/', views.update_macie_daily),
    path('update_download_url/', views.update_download_url),
    path('update_clip_views/', views.update_clip_views),
    path('ajax_macie/', views.ajax_macie),
    path('download_clips/', views.download_videos),
    path('dashboard/', views.dashboard),
    path('update_macie_all/', views.update_macie_all),
]
