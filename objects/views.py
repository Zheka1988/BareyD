from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from objects.models import Object
from references.models import Country, GovOrg, ForceType, ForceKind, Association, Unit


@login_required
def map_view(request):
    return render(request, 'index.html')


@login_required
def api_markers(request):
    objects = Object.objects.select_related(
        'country', 'gov_org', 'type', 'kind', 'association', 'unit'
    ).all()

    data = []
    for obj in objects:
        lat, lng = None, None
        geom_json = None

        if obj.latitude is not None and obj.longitude is not None:
            lat, lng = obj.latitude, obj.longitude
        elif obj.point is not None:
            lat, lng = obj.point.y, obj.point.x
        elif obj.geom is not None:
            geom_json = obj.geom.geojson

        data.append({
            'id': obj.pk,
            'name': str(obj),
            'description': obj.description or '',
            'lat': lat,
            'lng': lng,
            'geom': geom_json,
            'country': obj.country_id,
            'gov_org': obj.gov_org_id,
            'type': obj.type_id,
            'kind': obj.kind_id,
            'association': obj.association_id,
            'unit': obj.unit_id,
            'country_name': str(obj.country) if obj.country else '',
            'gov_org_name': str(obj.gov_org) if obj.gov_org else '',
            'type_name': str(obj.type) if obj.type else '',
            'kind_name': str(obj.kind) if obj.kind else '',
            'association_name': str(obj.association) if obj.association else '',
            'unit_name': str(obj.unit) if obj.unit else '',
        })

    return JsonResponse(data, safe=False)


@login_required
def api_filters(request):
    def qs_to_list(qs):
        return list(qs.values('id', 'name'))

    country_ids = request.GET.get('country')
    if country_ids:
        ids = [int(x) for x in country_ids.split(',') if x.strip().isdigit()]
        from django.db.models import Q
        country_filter = Q(country_id__in=ids) | Q(country__isnull=True)
        return JsonResponse({
            'country': qs_to_list(Country.objects.all()),
            'gov_org': qs_to_list(GovOrg.objects.filter(country_filter)),
            'type': qs_to_list(ForceType.objects.filter(country_filter)),
            'kind': qs_to_list(ForceKind.objects.filter(country_filter)),
            'association': qs_to_list(Association.objects.filter(country_filter)),
            'unit': qs_to_list(Unit.objects.filter(country_filter)),
        })

    return JsonResponse({
        'country': qs_to_list(Country.objects.all()),
        'gov_org': qs_to_list(GovOrg.objects.all()),
        'type': qs_to_list(ForceType.objects.all()),
        'kind': qs_to_list(ForceKind.objects.all()),
        'association': qs_to_list(Association.objects.all()),
        'unit': qs_to_list(Unit.objects.all()),
    })
