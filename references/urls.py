from django.urls import path
from .views import (
    GovOrgAutocomplete, ForceTypeAutocomplete, ForceKindAutocomplete,
    AssociationAutocomplete, UnitAutocomplete,
)

app_name = 'references'

urlpatterns = [
    path('autocomplete/gov-org/', GovOrgAutocomplete.as_view(), name='govorg-autocomplete'),
    path('autocomplete/force-type/', ForceTypeAutocomplete.as_view(), name='forcetype-autocomplete'),
    path('autocomplete/force-kind/', ForceKindAutocomplete.as_view(), name='forcekind-autocomplete'),
    path('autocomplete/association/', AssociationAutocomplete.as_view(), name='association-autocomplete'),
    path('autocomplete/unit/', UnitAutocomplete.as_view(), name='unit-autocomplete'),
]
