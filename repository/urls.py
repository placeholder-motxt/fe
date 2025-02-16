from django.urls import path

from repository.views import *

app_name = "repository"

urlpatterns = [
    path('', home, name="home"),
    path('/move-folder', async_move_folder, name="movefolder"),
    path('/create-folder', async_create_folder, name="createfolder"),
    path('/create-diagram', async_create_diagram, name="creatediagram"),
    path('/delete-folder', async_delete_folder, name="deletefolder"),
    path('/delete-diagram', async_delete_diagram, name="deletediagram"),
    path('/edit-folder', async_edit_diagram, name="editfolder"),
    path('/edit-diagram', async_delete_diagram, name="editdiagram"),
]
