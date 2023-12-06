class OrganizerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user_is_organizer = Organizer.objects.filter(
            user=self.request.user).exists()
        print(user_is_organizer)
        if user_is_organizer:
            user_organization = Organizer.objects.get(
                user=self.request.user).organization
            print(user_organization)
            country_organization = self.get_queryset().first().organization

            return user_organization == country_organization
        else:
            return False


class CountryListView(OrganizerRequiredMixin, ListView):
    model = Country
    template_name = 'configuration/option/country_list.html'
    context_object_name = 'countries'
