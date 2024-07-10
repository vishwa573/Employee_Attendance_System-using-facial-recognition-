from django.urls import path
from .import views

urlpatterns =[
    path('capture/<int:employee_id>/', views.capture_image, name='capture_image'),
    path('recognise_face/<int:employee_id>/', views.recognise, name='recognise'),
    path('updating_image_of_employee_/<int:employee_id>/',views.update_image,name='update_img')
]