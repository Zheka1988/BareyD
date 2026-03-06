from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('objects', '0002_alter_object_latitude_alter_object_longitude'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Association',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=200, verbose_name='Название')),
                        ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                    ],
                    options={
                        'verbose_name': 'Ассоциация',
                        'verbose_name_plural': 'Ассоциации',
                        'ordering': ['name'],
                    },
                ),
                migrations.CreateModel(
                    name='Country',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=200, verbose_name='Название')),
                    ],
                    options={
                        'verbose_name': 'Страна',
                        'verbose_name_plural': 'Страны',
                        'ordering': ['name'],
                    },
                ),
                migrations.CreateModel(
                    name='ForceKind',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=200, verbose_name='Название')),
                        ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                    ],
                    options={
                        'verbose_name': 'Вид сил',
                        'verbose_name_plural': 'Виды сил',
                        'ordering': ['name'],
                    },
                ),
                migrations.CreateModel(
                    name='ForceType',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=200, verbose_name='Название')),
                        ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                    ],
                    options={
                        'verbose_name': 'Тип сил',
                        'verbose_name_plural': 'Типы сил',
                        'ordering': ['name'],
                    },
                ),
                migrations.CreateModel(
                    name='GovOrg',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=200, verbose_name='Название')),
                        ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                    ],
                    options={
                        'verbose_name': 'Гос. орган',
                        'verbose_name_plural': 'Гос. органы',
                        'ordering': ['name'],
                    },
                ),
                migrations.CreateModel(
                    name='Unit',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=200, verbose_name='Название')),
                        ('description', models.TextField(blank=True, null=True, verbose_name='Описание')),
                    ],
                    options={
                        'verbose_name': 'Часть',
                        'verbose_name_plural': 'Части',
                        'ordering': ['name'],
                    },
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    'ALTER TABLE objects_association RENAME TO references_association',
                    'ALTER TABLE references_association RENAME TO objects_association',
                ),
                migrations.RunSQL(
                    'ALTER TABLE objects_country RENAME TO references_country',
                    'ALTER TABLE references_country RENAME TO objects_country',
                ),
                migrations.RunSQL(
                    'ALTER TABLE objects_forcekind RENAME TO references_forcekind',
                    'ALTER TABLE references_forcekind RENAME TO objects_forcekind',
                ),
                migrations.RunSQL(
                    'ALTER TABLE objects_forcetype RENAME TO references_forcetype',
                    'ALTER TABLE references_forcetype RENAME TO objects_forcetype',
                ),
                migrations.RunSQL(
                    'ALTER TABLE objects_govorg RENAME TO references_govorg',
                    'ALTER TABLE references_govorg RENAME TO objects_govorg',
                ),
                migrations.RunSQL(
                    'ALTER TABLE objects_unit RENAME TO references_unit',
                    'ALTER TABLE references_unit RENAME TO objects_unit',
                ),
            ],
        ),
    ]
