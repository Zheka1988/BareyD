from django.urls import path
from . import views

app_name = "objects"

urlpatterns = [
    path("", views.index, name="index"),
    path("tree", views.tree_data, name="tree"),
    path("markers", views.markers_data, name="markers"),
    path("node_objects", views.node_objects, name="node_objects"),
    path("add_object", views.add_object, name="add_object"),
    path("update_object/<int:obj_id>", views.update_object, name="update_object"),
    path("delete_object/<int:obj_id>", views.delete_object, name="delete_object"),
    path("hierarchy", views.hierarchy, name="hierarchy"),
    path("add_hierarchy", views.add_hierarchy, name="add_hierarchy"),
    path("add-object-form/", views.add_object_form, name="add_object_form"),
]
