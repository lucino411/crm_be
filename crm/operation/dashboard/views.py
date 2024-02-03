from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from administration.organization.models import Organization

@login_required
def dashboard(request, organization_slug=None):
    context = {'title': 'Dashboard'}
    return render(request, 'operation/dashboard/dashboard_home.html', context)


# @login_required
# def dashboard(request, organization_slug=None):
#     return render(request, 'operation/dashboard/dashboard_home.html')
