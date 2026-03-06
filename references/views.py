from dal import autocomplete
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import GovOrg, ForceType, ForceKind, Association, Unit


class CountryFilterAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    """Base autocomplete that filters by forwarded country value."""
    model = None

    def get_queryset(self):
        qs = self.model.objects.all()
        country = self.forwarded.get('country')
        if country:
            qs = qs.filter(Q(country_id=country) | Q(country__isnull=True))
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class GovOrgAutocomplete(CountryFilterAutocomplete):
    model = GovOrg


class ForceTypeAutocomplete(CountryFilterAutocomplete):
    model = ForceType


class ForceKindAutocomplete(CountryFilterAutocomplete):
    model = ForceKind


class AssociationAutocomplete(CountryFilterAutocomplete):
    model = Association


class UnitAutocomplete(CountryFilterAutocomplete):
    model = Unit
