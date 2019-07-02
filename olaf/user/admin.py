from django.contrib import admin

from leaflet.admin import LeafletGeoAdmin, LeafletGeoAdminMixin

from user.models import *


admin.site.register(FootNote)


class UserActivityAdmin(LeafletGeoAdmin):
    model = UserActivity
    readonly_fields = ('user', 'date')
    fields = ('user', 'date', 'gis_location')

admin.site.register(UserActivity, UserActivityAdmin)


class FootNoteInline(admin.TabularInline):
    model = FootNote
    extra = 1
    can_delete = False


class DeviceInline(admin.TabularInline):
    readonly_fields = ('device_id',)
    model = Device
    can_delete = False


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    can_delete = False


class UserActivityInline(LeafletGeoAdminMixin, admin.TabularInline):
    model = UserActivity
    can_delete = False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ('password',)

    inlines = (
        UserProfileInline,
        UserActivityInline,
        DeviceInline,
        FootNoteInline
    )

    list_filter = (
        'date_joined',
        'is_staff',
        'is_superuser',
        'is_business',
    )

    list_display = (
        'date_joined',
        'phone_number',
        'full_name',
        'email_address',
        'is_staff',
        'is_superuser',
        'is_business',
    )

    list_display_links = ('phone_number',)

    def full_name(self, object):
        return object.profile.full_name or 'Name not set'

    def email_address(self, object):
        return object.profile.email_address or 'Email not set'
