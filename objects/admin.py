from leaflet.admin import LeafletGeoAdmin
from django.contrib import admin
from django import forms
from dal import autocomplete
from .models import Object


class ObjectForm(forms.ModelForm):
    class Meta:
        model = Object
        fields = '__all__'
        widgets = {
            'gov_org': autocomplete.ModelSelect2(
                url='references:govorg-autocomplete',
                forward=['country'],
            ),
            'type': autocomplete.ModelSelect2(
                url='references:forcetype-autocomplete',
                forward=['country'],
            ),
            'kind': autocomplete.ModelSelect2(
                url='references:forcekind-autocomplete',
                forward=['country'],
            ),
            'association': autocomplete.ModelSelect2(
                url='references:association-autocomplete',
                forward=['country'],
            ),
            'unit': autocomplete.ModelSelect2(
                url='references:unit-autocomplete',
                forward=['country'],
            ),
        }


@admin.register(Object)
class ObjectAdmin(LeafletGeoAdmin):
    form = ObjectForm
    list_display = ["name", "short_name", "country", "gov_org", "type",
                    "kind", "association", "unit"]
    list_display_links = ["name"]
    search_fields = ["name", "short_name"]
    list_filter = ["country", "gov_org", "type", "kind", "association", "unit"]
    autocomplete_fields = ["country"]
    fieldsets = (
        (None, {
            "fields": ("name", "short_name", "description", "picture"),
        }),
        ("Классификация", {
            "fields": ("country", "gov_org", "type", "kind", "association", "unit"),
        }),
        ("Геометрия", {
            "fields": ("latitude", "longitude", "point", "geom"),
        }),
    )
