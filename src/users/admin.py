from django.contrib import admin

from users.models import User, UserEventLog

from users.use_cases import CreateUserRequest, CreateUser


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "is_staff", "is_active", "first_name", "last_name")
    list_filter = ("id", "email", "is_staff", "is_active", "first_name", "last_name")

    def save_model(self, request, obj, form, change):
        if change:
            super().save_model(request, obj, form, change)
        else:
            create_user_uc = CreateUser()
            response = create_user_uc.execute(CreateUserRequest(
                email=obj.email,
                first_name=obj.first_name,
                last_name=obj.last_name,
            ))
            if response.error:
                raise ValueError(response.error)


@admin.register(UserEventLog)
class UserEventLogAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "processed",)