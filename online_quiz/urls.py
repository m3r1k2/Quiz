# online_quiz/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import HomeView  # 👈 ВАЖНО

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView, name='home'),  # 👈 БЕЗ ()
    path('accounts/', include('accounts.urls')),
    path('quiz/', include('quiz.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )