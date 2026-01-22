from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home   # 👈 функция, НЕ класс

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name="home"),
    path('accounts/', include('accounts.urls')),
    path('quiz/', include('quiz.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
