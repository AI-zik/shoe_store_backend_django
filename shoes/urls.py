from django.urls import path
from .views import (AvailableShoeSizeDetailView, AvailableShoeSizeListView, 
CategoryDetailView, CategoryListView, ShoeDetailView, ShoeFeatureListCreateView, ShoeFeatureUpdateDeleteView, ShoeImageDetailView, 
ShoeImageListView, ShoeListView, ShoeRatingView, ShoeSizeUpdateDeleteView, ShoeSizeView, ShoeCategoryView)
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path("", ShoeListView.as_view(), name="shoe_list"),
    path("<int:id>/", ShoeDetailView.as_view(), name="shoe_detail"),

    path("<int:shoe_id>/images/", ShoeImageListView.as_view(), name="shoe_images"),
    path("<int:shoe_id>/images/<int:image_id>/", ShoeImageDetailView.as_view(),  name="shoe_image"),

    path("<int:shoe_id>/features/", ShoeFeatureListCreateView.as_view(), name='available_sizes'),
    path("<int:shoe_id>/features/<int:feature_id>/", ShoeFeatureUpdateDeleteView.as_view(), name='available_size'),

    path("<int:shoe_id>/categories/", ShoeCategoryView.as_view(), name="shoe_categories"),

    path("<int:shoe_id>/sizes/", AvailableShoeSizeListView.as_view(), name='available_sizes'),
    path("<int:shoe_id>/sizes/<int:size_id>/", AvailableShoeSizeDetailView.as_view(), name='available_size'),

    path("<int:shoe_id>/ratings/", ShoeRatingView.as_view(), name='shoe_ratings'),
    
    path("sizes/", ShoeSizeView.as_view(), name="sizes"),
    path("sizes/<int:size_id>/", ShoeSizeUpdateDeleteView.as_view(), name="size"),

    path("categories/", CategoryListView.as_view(), name="categories"),
    path("categories/<int:category_id>/", CategoryDetailView.as_view(), name="category"),

]

urlpatterns = format_suffix_patterns(urlpatterns)