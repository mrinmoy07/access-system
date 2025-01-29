# from django.urls import path
# from .views import face_registration, match_face

# urlpatterns = [
#     path('api/face-registration/', face_registration, name='face_registration'),
#     path('api/match-face/', match_face, name='match_face'),
# ]

# from django.urls import path
# from .views import face_registration, match_face, list_entries, search_entries

# urlpatterns = [
#     path('api/face-registration/', face_registration, name='face_registration'),
#     path('api/match-face/', match_face, name='match_face'),
#     path('entry-exit/', list_entries, name='list_entries'),
#     path('entry-exit/search/', search_entries, name='search_entries'),
# ]



from django.urls import path
from .views import face_registration, match_face, list_entries, search_entries, user_list, face_list, user_entry_exit_list,schedule_list, attendance_list

urlpatterns = [
    path('api/face-registration/', face_registration, name='face_registration'),
    path('api/match-face/', match_face, name='match_face'),
    path('entry-exit/', list_entries, name='list_entries'),
    path('entry-exit/search/', search_entries, name='search_entries'),
    path('users/', user_list, name='user_list'),
    path('faces/', face_list, name='face_list'),
    path('entries/', user_entry_exit_list, name='user_entry_exit_list'),
    path('schedules/', schedule_list, name='schedule_list'),
    path('attendance/', attendance_list, name='attendance_list'),
]

