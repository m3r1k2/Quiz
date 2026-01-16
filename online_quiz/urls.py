
from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
def main_page(request):
    return render(request, 'main.html')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main_page, name='main'),
    path('accounts/', include('accounts.urls')),
    path("quiz/", include("quiz.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

