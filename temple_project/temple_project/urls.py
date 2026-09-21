from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("festival.urls")),
]

if settings.DEBUG:
    # django.contrib.staticfiles already auto-serves STATIC_URL when
    # DEBUG=True and `runserver` is used, so only MEDIA needs wiring here.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
