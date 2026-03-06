from django.contrib import admin
from django.db.models import Q
from .models import Country, GovOrg, ForceType, ForceKind, Association, Unit


class CountryFilterMixin:
    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(request, queryset, search_term)
        country_id = request.GET.get('country_id')
        if country_id:
            queryset = queryset.filter(Q(country_id=country_id) | Q(country__isnull=True))
        return queryset, may_have_duplicates


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(GovOrg)
class GovOrgAdmin(CountryFilterMixin, admin.ModelAdmin):
    list_display = ["name", "country", "description"]
    list_filter = ["country"]
    search_fields = ["name"]
    autocomplete_fields = ["country"]


@admin.register(ForceType)
class ForceTypeAdmin(CountryFilterMixin, admin.ModelAdmin):
    list_display = ["name", "country", "description"]
    list_filter = ["country"]
    search_fields = ["name"]
    autocomplete_fields = ["country"]


@admin.register(ForceKind)
class ForceKindAdmin(CountryFilterMixin, admin.ModelAdmin):
    list_display = ["name", "country", "description"]
    list_filter = ["country"]
    search_fields = ["name"]
    autocomplete_fields = ["country"]


@admin.register(Association)
class AssociationAdmin(CountryFilterMixin, admin.ModelAdmin):
    list_display = ["name", "country", "description"]
    list_filter = ["country"]
    search_fields = ["name"]
    autocomplete_fields = ["country"]


@admin.register(Unit)
class UnitAdmin(CountryFilterMixin, admin.ModelAdmin):
    list_display = ["name", "country", "description"]
    list_filter = ["country"]
    search_fields = ["name"]
    autocomplete_fields = ["country"]
