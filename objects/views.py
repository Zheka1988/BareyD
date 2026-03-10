from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

from auditlog.models import AuditLog
from auditlog.utils import log_action
from objects.models import Object
from references.models import Country, GovOrg, ForceType, ForceKind, Association, Unit


@login_required
def map_view(request):
    log_action(request, AuditLog.Action.VIEW, 'Просмотр карты')
    return render(request, 'index.html')


def _serialize_objects(qs):
    data = []
    for obj in qs:
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
    return data


def _parse_ids(param):
    if not param:
        return []
    return [int(x) for x in param.split(',') if x.strip().isdigit()]


@login_required
def api_markers(request):
    qs = Object.objects.select_related(
        'country', 'gov_org', 'type', 'kind', 'association', 'unit'
    )

    filter_map = {
        'country': 'country_id__in',
        'gov_org': 'gov_org_id__in',
        'type': 'type_id__in',
        'kind': 'kind_id__in',
        'association': 'association_id__in',
        'unit': 'unit_id__in',
    }

    has_filters = False
    for param, lookup in filter_map.items():
        ids = _parse_ids(request.GET.get(param))
        if ids:
            qs = qs.filter(**{lookup: ids})
            has_filters = True

    if not has_filters:
        return JsonResponse({'objects': [], 'total': Object.objects.count()})

    exclude = _parse_ids(request.GET.get('exclude'))
    if exclude:
        qs = qs.exclude(pk__in=exclude)

    active = {p: request.GET.get(p) for p in filter_map if request.GET.get(p)}
    log_action(request, AuditLog.Action.FILTER, f'Фильтрация: {active}')

    total = Object.objects.count()
    data = _serialize_objects(qs)
    return JsonResponse({'objects': data, 'total': total})


@login_required
def api_search(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse([], safe=False)

    qs = Object.objects.select_related(
        'country', 'gov_org', 'type', 'kind', 'association', 'unit'
    ).filter(name__icontains=q)[:20]

    log_action(request, AuditLog.Action.SEARCH, f'Поиск: {q}')
    return JsonResponse(_serialize_objects(qs), safe=False)


@login_required
def api_filters(request):
    def qs_to_list(qs):
        return list(qs.values('id', 'name'))

    country_ids = request.GET.get('country')
    if country_ids:
        ids = _parse_ids(country_ids)
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


@login_required
def api_log_export(request):
    fmt = request.GET.get('format', '?')
    count = request.GET.get('count', '?')
    log_action(request, AuditLog.Action.EXPORT, f'Экспорт {count} объектов в {fmt}')
    return JsonResponse({'ok': True})
