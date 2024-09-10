from courses.views import (CoursesHomeView,
                           SearchCourse,
                           CourseDetail,
                           AddComment,
                           SectorCourse,
                           GetCartDetail,
                           CourseStudy)
from django.urls import path


urlpatterns = [
    path('cart/', GetCartDetail.as_view()),
    path('detail/<uuid:course_uuid>/', CourseDetail.as_view()),
    path('search/<str:search_term>/', SearchCourse.as_view()),
    path('study/<uuid:course_uuid>/', CourseStudy.as_view()),
    path('comment/<course_uuid>/', AddComment.as_view()),
    path('', CoursesHomeView.as_view()),
    path('<uuid:sector_uuid>/', SectorCourse.as_view()),
]