from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        success_url = reverse_lazy('dashboard-home')
        if hasattr(self.request.user, 'organizer'):
            organization_name = self.request.user.organizer.organization.name        
            success_url = reverse_lazy(
                'dashboard-home', kwargs={'organization_name': organization_name})
            messages.success(self.request, 'You have been logged in successfully as an Organizer.')
        elif hasattr(self.request.user, 'agent'):
            organization_name = self.request.user.agent.organization.name     
            success_url = reverse_lazy(
                'dashboard-home', kwargs={'organization_name': organization_name})
            messages.success(self.request, 'You have been logged in successfully as an Agent.')
        else:            
            messages.success(self.request, 'You have been logged in successfully.')
        return redirect(success_url)