from django.db import migrations


def normalize_application_stages(apps, schema_editor):
    Application = apps.get_model("jobs", "Application")
    Application.objects.filter(status="SUBMITTED").update(status="APPLIED")
    Application.objects.filter(status="REVIEWED").update(status="SCREENED")
    Application.objects.filter(status="ACCEPTED").update(status="HIRED")


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0005_application_kanban_statuses"),
    ]

    operations = [
        migrations.RunPython(
            normalize_application_stages,
            migrations.RunPython.noop,
        ),
    ]
