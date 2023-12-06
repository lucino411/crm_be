from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def dashboard(request, organization_name=None):
    context = {'organization_name': organization_name}
    return render(request, 'operation/dashboard/dashboard_home.html', context)
