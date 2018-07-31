from django.conf.urls import url
from users import views


app_name = 'users'
urlpatterns = [
    url(r'^register/', views.register, name='register'),
]
