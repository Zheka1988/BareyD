from django.db.models import F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET
# from django.views.decorators.csrf import csrf_exempt  # Убираем, будем использовать CSRF-токен из формы

from .models import (
    Object, Country, GovOrg, ForceType, ForceKind, Association, Unit
)

ALLOWED_HIERARCHY_MODELS = {
    "countries": Country,
    "gov_orgs": GovOrg,
    "force_types": ForceType,
    "force_kinds": ForceKind,
    "associations": Association,
    "units": Unit,
}


def add_object_form(request):
    # Собираем данные справочников напрямую
    context = {
        'countries': Country.objects.order_by('name').values('id', 'name'),
        'gov_orgs': GovOrg.objects.order_by('name').values('id', 'name'),
        'force_types': ForceType.objects.order_by('name').values('id', 'name'),
        'force_kinds': ForceKind.objects.order_by('name').values('id', 'name'),
        'associations': Association.objects.order_by('name').values('id', 'name'),
        'units': Unit.objects.order_by('name').values('id', 'name'),
    }
    return render(request, 'objects/partials/add_object_form.html', context)


def get_objects_qs():
    """Базовый queryset с джойнами"""
    return Object.objects.select_related(
        'country', 'gov_org', 'type', 'kind', 'association', 'unit'
    ).values(
        'id', 'name', 'short_name', 'latitude', 'longitude', 'description',
        'country_id', 'gov_org_id', 'type_id', 'kind_id', 'association_id', 'unit_id',
        country_name=F('country__name'),
        gov_org_name=F('gov_org__name'),
        type_name=F('type__name'),
        kind_name=F('kind__name'),
        association_name=F('association__name'),
        unit_name=F('unit__name'),
    )


def build_tree_and_map():
    """Строит плоский список для jstree + маппинги"""
    objects = list(get_objects_qs())

    tree = []
    node_ids = {}
    node_to_objects = {}  # node_id → set(object_ids)
    obj_to_leaf_node = {}  # object_id → leaf node_id (имя объекта)

    for obj in objects:
        obj_id = obj['id']
        path = (
            obj['country_name'],
            obj['gov_org_name'],
            obj['type_name'],
            obj['kind_name'],
            obj['association_name'],
            obj['unit_name'],
            obj['name'],
        )
        parent = "#"
        for name in path:
            if not name:
                continue
            key = (parent, name)
            if key not in node_ids:
                node_id = str(len(node_ids) + 1)  # или uuid, или hash, но просто счётчик
                tree.append({"id": node_id, "parent": parent, "text": name})
                node_ids[key] = node_id
                node_to_objects[node_id] = set()
            current_node = node_ids[key]
            node_to_objects[current_node].add(obj_id)
            parent = current_node

        if parent != "#":
            obj_to_leaf_node[obj_id] = parent

    return tree, node_to_objects, obj_to_leaf_node


@require_GET
def index(request):
    return render(request, "objects/index.html")


@require_GET
def tree_data(request):
    tree, _, _ = build_tree_and_map()
    return JsonResponse(tree, safe=False)


@require_GET
def markers_data(request):
    objects = list(get_objects_qs())
    _, _, obj_to_leaf_node = build_tree_and_map()

    markers = []
    for obj in objects:
        markers.append({
            "id": obj["id"],
            "name": obj["name"],
            "short_name": obj["short_name"],
            "lat": obj["latitude"],
            "lng": obj["longitude"],
            "country_id": obj["country_id"],
            "gov_org_id": obj["gov_org_id"],
            "type_id": obj["type_id"],
            "kind_id": obj["kind_id"],
            "association_id": obj["association_id"],
            "unit_id": obj["unit_id"],
            "description": obj["description"],
            "country_name": obj["country_name"],
            "gov_org_name": obj["gov_org_name"],
            "type_name": obj["type_name"],
            "kind_name": obj["kind_name"],
            "association_name": obj["association_name"],
            "unit_name": obj["unit_name"],
            "tree_node_id": obj_to_leaf_node.get(obj["id"]),
        })
    return JsonResponse(markers, safe=False)


@require_GET
def node_objects(request):
    node_id = request.GET.get("node_id")
    if not node_id:
        return JsonResponse([])

    _, node_to_objects, _ = build_tree_and_map()
    ids = list(node_to_objects.get(node_id, set()))
    return JsonResponse(ids, safe=False)


@require_POST
def add_object(request):
    data = request.POST
    
    # Если данные пришли через JSON (хотя форма шлет POST)
    if not data and request.content_type == 'application/json':
        import json
        data = json.loads(request.body)

    required = {"name", "lat", "lng"}
    if not all(k in data and data.get(k) not in (None, "") for k in required):
        return HttpResponse('<div class="text-red-600">Ошибка: Заполните обязательные поля</div>', status=400)

    try:
        obj = Object.objects.create(
            country_id=data.get("country_id") or None,
            gov_org_id=data.get("gov_org_id") or None,
            type_id=data.get("type_id") or None,
            kind_id=data.get("kind_id") or None,
            association_id=data.get("association_id") or None,
            unit_id=data.get("unit_id") or None,
            name=data["name"],
            short_name=data.get("short_name", ""),
            latitude=float(data["lat"]),
            longitude=float(data["lng"]),
            description=data.get("description", ""),
        )
        
        response = HttpResponse('<div class="text-green-600">Объект успешно добавлен!</div>')
        response["HX-Trigger"] = "objectAdded"
        return response
    except Exception as e:
        return HttpResponse(f'<div class="text-red-600">Ошибка: {str(e)}</div>', status=500)


@require_POST
def update_object(request, obj_id):
    try:
        obj = Object.objects.get(id=obj_id)
    except Object.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Object not found"}, status=404)

    data = request.POST or request.json()

    allowed = {
        "name", "short_name", "lat", "lng", "description",
        "country_id", "gov_org_id", "type_id", "kind_id", "association_id", "unit_id"
    }
    mapping = {"lat": "latitude", "lng": "longitude"}

    updated = False
    for k, v in data.items():
        if k not in allowed:
            continue
        field = mapping.get(k, k)
        if hasattr(obj, field):
            setattr(obj, field, v)
            updated = True

    if updated:
        obj.save()

    return JsonResponse({"status": "ok"})


@require_POST
def delete_object(request, obj_id):
    Object.objects.filter(id=obj_id).delete()
    return JsonResponse({"status": "ok"})


@require_GET
def hierarchy(request):
    data = {}
    for key, Model in ALLOWED_HIERARCHY_MODELS.items():
        data[key] = list(Model.objects.order_by("name").values("id", "name"))
    return JsonResponse(data)


@require_POST
def add_hierarchy(request):
    data = request.POST or request.json()
    table = data.get("table")
    name = data.get("name")

    if not table or not name:
        return JsonResponse({"status": "error", "message": "Не указана таблица или имя"}, status=400)

    Model = ALLOWED_HIERARCHY_MODELS.get(table)
    if not Model:
        return JsonResponse({"status": "error", "message": "Недопустимая таблица"}, status=400)

    obj, created = Model.objects.get_or_create(name=name)
    return JsonResponse({"status": "ok", "id": obj.id})