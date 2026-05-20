from django.conf import settings
from django.db import migrations


def create_missing_profiles(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL.split(".")[0], settings.AUTH_USER_MODEL.split(".")[1])
    Profile = apps.get_model("accounts", "Profile")

    existing_profile_user_ids = set(Profile.objects.values_list("user_id", flat=True))
    profiles = [
        Profile(user_id=user_id)
        for user_id in User.objects.exclude(id__in=existing_profile_user_ids).values_list("id", flat=True)
    ]
    Profile.objects.bulk_create(profiles)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_profile_is_platform_admin_tutorapplication_and_more"),
    ]

    operations = [
        migrations.RunPython(create_missing_profiles, migrations.RunPython.noop),
    ]
