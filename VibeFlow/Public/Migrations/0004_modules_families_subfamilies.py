# Generated manually - adds modules, families, subfamilies tables
# and adds hierarchy FKs to view_routes.
# RoutePermission already has role_id in DB, just fix Django state.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_routepermission'),
    ]

    operations = [
        # ── Create modules table ──
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True, help_text='Nombre del módulo')),
                ('icon', models.CharField(default='📁', max_length=50, help_text='Icono emoji o clase CSS')),
                ('display_order', models.IntegerField(default=0, help_text='Orden de presentación')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'modules',
                'ordering': ['display_order', 'name'],
            },
        ),

        # ── Create families table ──
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, help_text='Nombre de la familia')),
                ('icon', models.CharField(default='📂', max_length=50, help_text='Icono emoji o clase CSS')),
                ('display_order', models.IntegerField(default=0, help_text='Orden de presentación')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(
                    help_text='Módulo al que pertenece',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='families',
                    to='accounts.module',
                )),
            ],
            options={
                'db_table': 'families',
                'ordering': ['display_order', 'name'],
                'unique_together': {('module', 'name')},
            },
        ),

        # ── Create subfamilies table ──
        migrations.CreateModel(
            name='Subfamily',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, help_text='Nombre de la subfamilia')),
                ('icon', models.CharField(default='📄', max_length=50, help_text='Icono emoji o clase CSS')),
                ('display_order', models.IntegerField(default=0, help_text='Orden de presentación')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('family', models.ForeignKey(
                    help_text='Familia a la que pertenece',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subfamilies',
                    to='accounts.family',
                )),
            ],
            options={
                'db_table': 'subfamilies',
                'ordering': ['display_order', 'name'],
                'unique_together': {('family', 'name')},
            },
        ),

        # ── Add hierarchy FKs to view_routes ──
        migrations.AddField(
            model_name='viewroute',
            name='module',
            field=models.ForeignKey(
                blank=True, null=True,
                help_text='Módulo al que pertenece (nivel 1)',
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='routes',
                to='accounts.module',
            ),
        ),
        migrations.AddField(
            model_name='viewroute',
            name='family',
            field=models.ForeignKey(
                blank=True, null=True,
                help_text='Familia a la que pertenece (nivel 2)',
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='routes',
                to='accounts.family',
            ),
        ),
        migrations.AddField(
            model_name='viewroute',
            name='subfamily',
            field=models.ForeignKey(
                blank=True, null=True,
                help_text='Subfamilia a la que pertenece (nivel 3)',
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='routes',
                to='accounts.subfamily',
            ),
        ),

        # ── Fix RoutePermission Django state ──
        # DB already has role_id, not user_id.
        # Use SeparateDatabaseAndState to update Django's state without touching DB.
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='routepermission',
                    name='user',
                ),
                migrations.AddField(
                    model_name='routepermission',
                    name='role',
                    field=models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='route_permissions',
                        to='accounts.role',
                        db_column='role_id',
                    ),
                    preserve_default=False,
                ),
                migrations.AlterUniqueTogether(
                    name='routepermission',
                    unique_together={('role', 'route')},
                ),
                migrations.AlterModelOptions(
                    name='routepermission',
                    options={'ordering': ['route__url_path', 'role__name']},
                ),
            ],
            database_operations=[],
        ),
    ]
