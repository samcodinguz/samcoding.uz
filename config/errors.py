from django.shortcuts import render

def error_400(request, exception=None):
    return render(request, 'core/public/errors/400.html', status=400)

def error_401(request, exception=None):
    return render(request, 'core/public/errors/401.html', status=401)

def error_402(request, exception=None):
    return render(request, 'core/public/errors/402.html', status=402)

def error_403(request, exception=None):
    return render(request, 'core/public/errors/403.html', status=403)

def error_404(request, exception=None):
    return render(request, 'core/public/errors/404.html', status=404)

def error_408(request, exception=None):
    return render(request, 'core/public/errors/408.html', status=408)

def error_500(request):
    return render(request, 'core/public/errors/500.html', status=500)