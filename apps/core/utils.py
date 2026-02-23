from datetime import datetime

def get_base_context(request):

    return {
        'current_year': datetime.now().year
    }