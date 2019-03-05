from .state import state as current_state


def state(request):
    return {'state': current_state}
