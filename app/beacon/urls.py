from django.urls import path

from . import views

app_name = 'beacon'
urlpatterns = [
    path('', views.variant, name='variant'),
    path('variant', views.variant, name='variant'),
    path('variant_response', views.variant_response, name='variant_response'),
    path('region', views.region, name='region'),
    path('region_response', views.region_response, name='region_response'),
    path('phenoclinic', views.phenoclinic, name='phenoclinic'),
    path('phenoclinic_response', views.phenoclinic_response, name='phenoclinic_response'),
    path('cohorts', views.cohorts, name='cohorts'),
    path('query_help', views.query_help, name='query_help'),
    path('api_help', views.api_help, name='api_help'),
    path('filtering_terms', views.filtering_terms, name='filtering_terms'),
]