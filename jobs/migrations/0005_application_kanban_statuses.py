from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0004_alter_application_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="status",
            field=models.CharField(
                choices=[
                    ("APPLIED", "Applied"),
                    ("SCREENED", "Screened"),
                    ("INTERVIEWED", "Interviewed"),
                    ("OFFERED", "Offered"),
                    ("HIRED", "Hired"),
                    ("CLOSED", "Closed"),
                    ("DELETED", "Deleted"),
                    ("REJECTED", "Rejected"),
                    ("WITHDRAWN", "Withdrawn"),
                    ("SUBMITTED", "Submitted"),
                    ("REVIEWED", "Reviewed"),
                    ("ACCEPTED", "Accepted"),
                ],
                default="APPLIED",
                max_length=12,
            ),
        ),
    ]
