from django.urls import path
from . import views

urlpatterns = [
    path('get-carms', views.get_carms),
    path('carm-images/<filename>', views.serve_carm_image),
    path('check-video-connection', views.check_video_connection),
    path('check-tilt-sensor', views.check_tilt_sensor),
    path('run2', views.start_processing),
    path('api/states', views.get_states),
    path('api/setting', views.set_ai_autocollect_modes),
    path('api/image-with-metadata', views.get_image_with_metadata),
    path('landmarks', views.save_landmarks),
    path('cap', views.manual_framecap),
    path('label', views.switch_side),
    path('edit', views.edit),
    path('next', views.next),
    path('restart', views.restart),
    path('screenshot/<int:stage>', views.save_screen),
    path('screenshot/<int:stage>', views.get_screen),
    path('stitch/<int:stage>', views.get_stitch),
    path('patient', views.patient),
    path('pdf', views.pdf),
]