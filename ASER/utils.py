# ASER/utils.py
from django.apps import apps

ENTITY_TYPE_MAP = {
    "hospitals": "hospitals.Hospital",
    "clincs":    "clincs.Clinic",
    "labs":      "labs.Lab",
    "doctors":   "doctors.Doctor",
}

def get_entity_model(entity_type: str):
    model_path = ENTITY_TYPE_MAP.get(entity_type)
    if not model_path:
        return None
    app_label, model_name = model_path.split(".")
    return apps.get_model(app_label, model_name)

def get_entity_for_user(user):
    """
    Returns (entity, entity_type) for a medical-entity user.
    Returns (None, None) for normal/community users.
    """
    if user.user_type not in ENTITY_TYPE_MAP:
        return None, None
    model = get_entity_model(user.user_type)
    try:
        return model.objects.get(user=user), user.user_type
    except model.DoesNotExist:
        return None, None

def get_entity_id_for_user(user):
    entity, _ = get_entity_for_user(user)
    return entity.id if entity else None