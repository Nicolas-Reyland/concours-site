from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _


class ProloginUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (_("Profil"), {'fields': ('address', 'postal_code', 'city', 'country', 'phone_number', 'birthday')}),
        (_("Préférences"), {'fields': ('newsletter',)}),
    )

admin.site.register(get_user_model(), ProloginUserAdmin)
