import decimal
import csv
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from .forms import StaffUserCreationForm, StaffUserChangeForm, PartyUserCreationForm, PartyUserChangeForm
from .models import Party, Property, Transaction, StaffUser, Inspection, TransactionAssignment, InspectionImage


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
                "email", "password1", "password2", "is_active", "first_name", "last_name",
                "identification", "phone_number", "natural_person", "address", "city", "post_code"
            )}
         ),
    )
    search_fields = ("phone_number",)
    ordering = ("phone_number",)
    filter_horizontal = ()


class PropertyAdmin(admin.ModelAdmin):
    actions = ['export_property']

    def export_property(modeladmin, request, queryset):

        # Create a CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="projects.csv"'

        # Create a CSV writer and write the header row
        csv_writer = csv.writer(response)
        csv_writer.writerow(
            ['Property Identifier', 'Area', 'Locality', 'District' 'Ownership type', 'Property type', 'Created At',])

        # Write data rows for selected projects
        for obj in queryset:
            csv_writer.writerow([
                obj.zupin,
                obj.area,
                obj.locality,
                obj.district,
                obj.get_ownership_type_display(),
                obj.get_property_type_display(),
                obj.created_at,

            ])

        return response

    export_property.short_description = 'Export properties to CSV'


admin.site.register(StaffUser, StaffUserAdmin)
admin.site.unregister(Group)
admin.site.register(Transaction)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Party, PartyUserAdmin)
admin.site.register(TransactionAssignment)
admin.site.register(Inspection)
admin.site.register(InspectionImage)

# admin.site.register(Ownership)
