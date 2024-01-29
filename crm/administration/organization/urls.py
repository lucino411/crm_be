from django.urls import path

# from administration.organization.views import upload_file_view
from .views import ImageUploadView, MediaLibraryView

app_name = 'organization'

urlpatterns = [
        path('upload/', ImageUploadView.as_view(), name='upload-file'),
        path('library/', MediaLibraryView.as_view(), name='media-library'),
        # path('upload/', upload_file_view, name='upload-file'),
]