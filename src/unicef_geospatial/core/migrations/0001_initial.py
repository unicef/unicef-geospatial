# Generated by Django 2.2b1 on 2019-03-12 08:57

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone
import django_fsm
import model_utils.fields
import mptt.fields
import unicef_geospatial.state.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Name')),
                ('description', models.CharField(blank=True, max_length=512, null=True, verbose_name='Description')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='core.Category', verbose_name='Parent')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='ConfigMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('creator', unicef_geospatial.state.fields.CreatorUserField(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('modifier', unicef_geospatial.state.fields.ModifierUserField(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('target', models.ForeignKey(limit_choices_to={'app_label': 'core', 'model__in': ['country', 'location', 'boundary']}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique id')),
                ('valid_from', models.DateTimeField(blank=True, null=True, verbose_name='start')),
                ('valid_to', models.DateTimeField(blank=True, null=True, verbose_name='end')),
                ('state', django_fsm.FSMField(choices=[('Pending Approval', 'Pending Approval'), ('Active', 'Active'), ('Archived', 'Archived')], default='Active', max_length=50, protected=True, verbose_name='Record State')),
                ('active', models.BooleanField(blank=True, default=True, null=True, verbose_name='Active')),
                ('name', models.CharField(db_index=True, max_length=127, verbose_name='Name')),
                ('fullname', models.CharField(blank=True, db_index=True, max_length=127, null=True, verbose_name='Full Name')),
                ('alternate_name', models.CharField(blank=True, db_index=True, max_length=127, null=True, verbose_name='Alternate Name')),
                ('iso_code_2', models.CharField(max_length=2, unique=True, verbose_name='ISO code 2')),
                ('iso_code_3', models.CharField(max_length=3, unique=True, verbose_name='ISO code 3')),
                ('un_number', models.CharField(blank=True, max_length=3, null=True, verbose_name='UN Number')),
                ('continent', models.CharField(choices=[('AF', 'Africa'), ('AN', 'Antartica'), ('AS', 'Asia'), ('EU', 'Europe'), ('NA', 'North America'), ('OC', 'Oceania'), ('SA', 'South America')], max_length=2)),
            ],
            options={
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', django_fsm.FSMField(choices=[('preparing', 'preparing'), ('ready', 'ready'), ('queued', 'queued'), ('in progress', 'in progress'), ('canceled', 'canceled'), ('failed', 'failed'), ('succeeded', 'succeeded')], default='preparing', max_length=50, protected=True, verbose_name='State')),
                ('country_field', models.CharField(blank=True, help_text='If Global set the name of the column that contains Country name', max_length=50, null=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('pattern_filter', models.CharField(default='*', max_length=10)),
                ('boundary_type_policy', models.CharField(choices=[('get', 'get'), ('get_or_create', 'get_or_create')], max_length=15)),
                ('country_policy', models.CharField(choices=[('get', 'get'), ('get_or_create', 'get_or_create')], max_length=15)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('mapping', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('confirm_required', models.BooleanField(default=False, help_text='Explicitly confirm publication after loading')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Country')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UploadFieldMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geo_field', models.CharField(max_length=255)),
                ('shape_field', models.CharField(max_length=255)),
                ('mandatory', models.BooleanField(default=True)),
                ('is_value', models.BooleanField(default=False)),
                ('update', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='core.Upload')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique id')),
                ('name_en', models.CharField(blank=True, max_length=127, null=True, verbose_name='English Name')),
                ('name_fr', models.CharField(blank=True, max_length=127, null=True, verbose_name='French Name')),
                ('name_es', models.CharField(blank=True, max_length=127, null=True, verbose_name='Spanish Name')),
                ('name_ar', models.CharField(blank=True, max_length=127, null=True, verbose_name='Arabic Name')),
                ('alternate_names', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('valid_from', models.DateTimeField(blank=True, null=True, verbose_name='start')),
                ('valid_to', models.DateTimeField(blank=True, null=True, verbose_name='end')),
                ('state', django_fsm.FSMField(choices=[('Pending Approval', 'Pending Approval'), ('Active', 'Active'), ('Archived', 'Archived')], default='Active', max_length=50, protected=True, verbose_name='Record State')),
                ('active', models.BooleanField(blank=True, default=True, null=True, verbose_name='Active')),
                ('name', models.CharField(db_index=True, max_length=127, verbose_name='Name')),
                ('p_code', models.CharField(blank=True, max_length=32, null=True, verbose_name='P Code')),
                ('point', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='Point')),
                ('is_active', models.BooleanField(blank=True, default=True, verbose_name='Active')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Category')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Country')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FieldMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geo_field', models.CharField(max_length=255)),
                ('shape_field', models.CharField(max_length=255)),
                ('mandatory', models.BooleanField(default=True)),
                ('config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ConfigMap')),
            ],
        ),
        migrations.CreateModel(
            name='BoundaryType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique id')),
                ('valid_from', models.DateTimeField(blank=True, null=True, verbose_name='start')),
                ('valid_to', models.DateTimeField(blank=True, null=True, verbose_name='end')),
                ('state', django_fsm.FSMField(choices=[('Pending Approval', 'Pending Approval'), ('Active', 'Active'), ('Archived', 'Archived')], default='Active', max_length=50, protected=True, verbose_name='Record State')),
                ('active', models.BooleanField(blank=True, default=True, null=True, verbose_name='Active')),
                ('description', models.CharField(max_length=250)),
                ('admin_level', models.IntegerField(choices=[(0, 'Level 0'), (1, 'Level 1'), (2, 'Level 2'), (3, 'Level 3'), (4, 'Level 4'), (5, 'Level 5')], verbose_name='Admin Level')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Country')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='core.BoundaryType', verbose_name='Parent')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('_tree_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Boundary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique id')),
                ('name_en', models.CharField(blank=True, max_length=127, null=True, verbose_name='English Name')),
                ('name_fr', models.CharField(blank=True, max_length=127, null=True, verbose_name='French Name')),
                ('name_es', models.CharField(blank=True, max_length=127, null=True, verbose_name='Spanish Name')),
                ('name_ar', models.CharField(blank=True, max_length=127, null=True, verbose_name='Arabic Name')),
                ('alternate_names', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('valid_from', models.DateTimeField(blank=True, null=True, verbose_name='start')),
                ('valid_to', models.DateTimeField(blank=True, null=True, verbose_name='end')),
                ('state', django_fsm.FSMField(choices=[('Pending Approval', 'Pending Approval'), ('Active', 'Active'), ('Archived', 'Archived')], default='Active', max_length=50, protected=True, verbose_name='Record State')),
                ('active', models.BooleanField(blank=True, default=True, null=True, verbose_name='Active')),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=4326, verbose_name='Geometry')),
                ('gender', models.CharField(choices=[('cod', 'COD'), ('global', 'Global')], max_length=15)),
                ('name', models.CharField(db_index=True, max_length=127, verbose_name='Name')),
                ('p_code', models.CharField(blank=True, max_length=32, null=True, verbose_name='P Code')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('boundary_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.BoundaryType')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Country')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='core.Boundary', verbose_name='Parent')),
            ],
            options={
                'verbose_name_plural': 'Admin Boundaries',
            },
            managers=[
                ('_tree_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddConstraint(
            model_name='boundary',
            constraint=models.UniqueConstraint(condition=models.Q(active=True), fields=('p_code', 'country', 'level', 'active'), name='unique_active_pcode'),
        ),
    ]
