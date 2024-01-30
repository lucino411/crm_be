from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        success_url = reverse_lazy('dashboard-home')
        if hasattr(self.request.user, 'organizer'):
            organization_slug = self.request.user.organizer.organization.slug        
            success_url = reverse_lazy(
                'dashboard-home', kwargs={'organization_slug': organization_slug})
            messages.success(self.request, 'You have been logged in successfully as an Organizer.')
        elif hasattr(self.request.user, 'agent'):
            organization_slug = self.request.user.agent.organization.slug     
            success_url = reverse_lazy(
                'dashboard-home', kwargs={'organization_slug': organization_slug})
            messages.success(self.request, 'You have been logged in successfully as an Agent.')
        else:            
            messages.success(self.request, 'You have been logged in successfully.')
        return redirect(success_url)