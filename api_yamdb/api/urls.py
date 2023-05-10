from api.v1.urls import v1_urlpatterns
from django.urls import include, path

urlpatterns = [
    path('v1/', include(v1_urlpatterns)),
]
