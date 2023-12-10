from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Organizer, Agent

''' 
/************
MIXINS
/************
'''

class OrganizerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user_is_organizer = Organizer.objects.filter(
            user=self.request.user, user__is_active=True).exists()
        return user_is_organizer

class OrganizerContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization_name'] = self.get_organization()
        return context

    def get_organization(self):
        return self.request.user.organizer.organization    

class AgentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user_is_agent = Agent.objects.filter(
            user=self.request.user, user__is_active=True).exists()
        return user_is_agent
    
class AgentContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organization_name'] = self.get_organization()
        return context

    def get_organization(self):
        return self.request.user.agent.organization

    
