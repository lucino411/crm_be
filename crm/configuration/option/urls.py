from django.urls import path
from .views import CountryListView, CountryDetailView, CountryCreateView, CountryUpdateView

app_name = 'configuration'

# urlpatterns = [
#     path('<str:organization_name>/configuration/option/country/',
#          CountryListView.as_view(), name='country-list'),
#     path('<str:organization_name>/configuration/option/country/<int:pk>/',
#          CountryDetailView.as_view(), name='country-detail'),
#     path('<str:organization_name>/configuration/option/country/create/',
#          CountryCreateView.as_view(), name='country-create'),
#     path('<str:organization_name>/configuration/option/country/<int:pk>/update/',
#          CountryUpdateView.as_view(), name='country-update'),
# ]

urlpatterns = [
    path('configuration/country/',
         CountryListView.as_view(), name='country-list'),
    path('configuration/option/country/<int:pk>/',
         CountryDetailView.as_view(), name='country-detail'),
    # path('<str:organization_name>/configuration/option/country/<int:pk>/',
    #      CountryDetailView.as_view(), name='country-detail'),
    # path('<str:organization_name>/configuration/option/country/create/',
    #      CountryCreateView.as_view(), name='country-create'),
    # path('<str:organization_name>/configuration/option/country/<int:pk>/update/',
    #      CountryUpdateView.as_view(), name='country-update'),
]


