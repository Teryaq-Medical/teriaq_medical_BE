# ASER/mixins.py
from .utils import get_entity_for_user

class EntityResolutionMixin:
    """
    Add to any ViewSet to get self.get_request_entity().
    Removes the repeated user_type branching from every viewset.
    """
    def get_request_entity(self):
        entity, entity_type = get_entity_for_user(self.request.user)
        return entity, entity_type