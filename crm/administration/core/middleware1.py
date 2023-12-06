from django.http import HttpResponseRedirect
from administration.userprofile.models import Organizer, Agent


# class OrganizationMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)

#         if request.user.is_authenticated:
#             try:
#                 organizer = Organizer.objects.get(user=request.user)
#                 organization_name = organizer.organization.name
#             except Organizer.DoesNotExist:
#                 try:
#                     agent = Agent.objects.get(user=request.user)
#                     organization_name = agent.organization.name
#                 except Agent.DoesNotExist:
#                     organization_name = None

#             if organization_name and not request.path_info.startswith(f"/{organization_name}/"):
#                 return HttpResponseRedirect(f"/{organization_name}{request.path_info}")

#         return response


from django.http import HttpResponseRedirect
from administration.userprofile.models import Organizer, Agent


class OrganizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path_info.startswith('/logout/'):
            response = self.process_request(request)
        else:
            response = self.get_response(request)

        return response

    def process_request(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            try:
                organizer = Organizer.objects.get(user=request.user)
                organization_name = organizer.organization.name
            except Organizer.DoesNotExist:
                try:
                    agent = Agent.objects.get(user=request.user)
                    organization_name = agent.organization.name
                except Agent.DoesNotExist:
                    organization_name = None

            if organization_name and not request.path_info.startswith(f"/{organization_name}/"):
                return HttpResponseRedirect(f"/{organization_name}{request.path_info}")

        return response
