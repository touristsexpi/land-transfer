from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from .forms import StaffUserCreationForm, StaffUserChangeForm, PartyUserCreationForm, PartyUserChangeForm
from .models import Party, Property, Transaction, StaffUser, Inspection, TransactionAssignment


class StaffUserAdmin(UserAdmin):
    add_form = StaffUserCreationForm
    form = StaffUserChangeForm
    model = StaffUser
    list_display = ("email", "is_staff", "is_active",)
    list_filter = ("email", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ('Personal info', {'fields': ()}),
        ("Permissions", {"fields": ("is_staff", "is_active",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "first_name", "last_name",
                "is_active", "department", "employee_id", "phone_number",
            )}
        ),
    )
    search_fields = ("phone_number",)
    ordering = ("phone_number",)
    filter_horizontal = ()

class PartyUserAdmin(UserAdmin):
    add_form = PartyUserCreationForm
    form = PartyUserChangeForm
    model = StaffUser
    list_display = ("email", "is_active",)
    list_filter = ("email", "is_active",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2","is_active", "first_name", "last_name",
                  "identification", "phone_number", "natural_person", "address", "city", "post_code"
            )}
        ),
    )
    search_fields = ("phone_number",)
    ordering = ("phone_number",)
    filter_horizontal = ()



admin.site.register(StaffUser, StaffUserAdmin)
admin.site.unregister(Group)
admin.site.register(Transaction)
admin.site.register(Property)
admin.site.register(Party, PartyUserAdmin)
admin.site.register(TransactionAssignment)
admin.site.register(Inspection)

# admin.site.register(Ownership)
