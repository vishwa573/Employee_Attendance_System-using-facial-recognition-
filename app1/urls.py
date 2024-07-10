from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('signin/', views.signin, name='signin'),
    path('validate_password/', views.validate_password, name='validate_password'),
    path('signout/', views.signout, name='signout'),
    path('manview/<int:manager_id>/<str:manager_name>/', views.manager_view, name='manview'),
    path('download_csv_attendance/<int:employee_id>', views.download, name='download'),
    path('',views.display,name='display'),
    path('Name_for_the_request_location/<int:employee_id>/<str:lat>/<str:long>/', views.loc_name, name='loc_name'),
    path('displayy/<int:manager_id>/<str:manager_name>/', views.displayy ,name='displayy'),
    path('rej_reg/<int:manager_id>/<str:manager_name>/', views.rejected_registerations ,name='rejected_registerations'),
    path('appr_reg/<int:manager_id>/<str:manager_name>/', views.approved_registerations ,name='approved_registerations'),
    path('upd_faces_requests/<int:manager_id>/<str:manager_name>/', views.update_faces ,name='update_faces'),
    path('upd_location_requests/<int:manager_id>/<str:manager_name>/', views.update_locations ,name='update_loc'),
    path('see_attendance_of_the_employees/<int:manager_id>/<str:manager_name>/', views.see_attendance ,name='see_attendance'),
    path('remove_employees/<int:manager_id>/<str:manager_name>/', views.remove_employees ,name='remove_employees'),
]