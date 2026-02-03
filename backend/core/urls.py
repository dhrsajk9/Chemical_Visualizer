from django.urls import path
from .views import FileUploadView, AnalyticsView, CustomAuthToken, PDFReportView

urlpatterns = [
    path('login/', CustomAuthToken.as_view()),
    path('files/', FileUploadView.as_view()),
    path('analytics/<int:pk>/', AnalyticsView.as_view()),
    path('pdf/<int:pk>/', PDFReportView.as_view()),
]