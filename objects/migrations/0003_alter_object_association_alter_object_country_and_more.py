import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objects', '0002_alter_object_latitude_alter_object_longitude'),
        ('references', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='object',
                    name='association',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='obj_association', to='references.association', verbose_name='Ассоциация'),
                ),
                migrations.AlterField(
                    model_name='object',
                    name='country',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='obj_country', to='references.country', verbose_name='Страна'),
                ),
                migrations.AlterField(
                    model_name='object',
                    name='kind',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='obj_kind', to='references.forcekind', verbose_name='Вид сил'),
                ),
                migrations.AlterField(
                    model_name='object',
                    name='type',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='obj_type', to='references.forcetype', verbose_name='Тип сил'),
                ),
                migrations.AlterField(
                    model_name='object',
                    name='gov_org',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='obj_gov_org', to='references.govorg', verbose_name='Гос. орган'),
                ),
                migrations.AlterField(
                    model_name='object',
                    name='unit',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='obj_unit', to='references.unit', verbose_name='Часть'),
                ),
                migrations.DeleteModel(
                    name='Association',
                ),
                migrations.DeleteModel(
                    name='Country',
                ),
                migrations.DeleteModel(
                    name='ForceKind',
                ),
                migrations.DeleteModel(
                    name='ForceType',
                ),
                migrations.DeleteModel(
                    name='GovOrg',
                ),
                migrations.DeleteModel(
                    name='Unit',
                ),
            ],
            database_operations=[],
        ),
    ]
