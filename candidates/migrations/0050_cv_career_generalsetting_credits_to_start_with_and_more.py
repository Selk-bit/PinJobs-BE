from django.db import migrations, connection

def add_columns_if_not_exist(apps, schema_editor):
    """
    Adds columns only if they don't already exist in MySQL.
    """
    with connection.cursor() as cursor:
        # Check if the column exists in candidates_cv
        cursor.execute("SHOW COLUMNS FROM candidates_cv LIKE 'career_id';")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE candidates_cv ADD COLUMN career_id INT;")

        # Check if the column exists in candidates_generalsetting
        cursor.execute("SHOW COLUMNS FROM candidates_generalsetting LIKE 'credits_to_start_with';")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE candidates_generalsetting ADD COLUMN credits_to_start_with INT DEFAULT 10;")

        cursor.execute("SHOW COLUMNS FROM candidates_generalsetting LIKE 'num_of_careers_to_generate';")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE candidates_generalsetting ADD COLUMN num_of_careers_to_generate INT DEFAULT 5;")


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0049_remove_answerset_group_identifier'),
    ]

    operations = [
        migrations.RunPython(add_columns_if_not_exist),
    ]
