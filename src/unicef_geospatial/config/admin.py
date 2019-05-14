from collections import OrderedDict

from django.conf import settings
from django.contrib.admin import AdminSite as _AdminSite
from django.contrib.admin.apps import SimpleAdminConfig
from django.core.cache import caches
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy
from django.views.decorators.cache import never_cache

from constance import config

from unicef_geospatial.utils.version import get_full_version

cache = caches['default']

DEFAULT_INDEX_SECTIONS = None


class AdminSite(_AdminSite):
    site_title = gettext_lazy('Geospatial site admin')

    site_header = gettext_lazy('Geospatial administration')

    @never_cache
    def index(self, request, extra_context=None):
        style = request.COOKIES.get('old_index_style', 0)
        if style in [1, "1"]:
            return super().index(request, {'index_style': 0})
        else:
            return self.index_new(request, {'index_style': 1})

    def get_index_sections(self, request):
        if DEFAULT_INDEX_SECTIONS is None:
            app_list = self.get_app_list(request)
            sections = OrderedDict()
            for entry in app_list:
                sections[entry['name']] = ['%s.%s' % (entry['app_label'], m['object_name']) for m in entry['models']]
            sections['Other'] = []
            sections['_hidden_'] = []
            return sections
        else:
            sections = OrderedDict(DEFAULT_INDEX_SECTIONS)
            sections.setdefault('Other', [])
            sections.setdefault('_hidden_', [])
            return sections

    @never_cache
    def index_new(self, request, extra_context=None):
        key = f'apps_groups:{request.user.id}:{get_full_version()}:{config.CACHE_VERSION}'
        app_list = self.get_app_list(request)
        groups = cache.get(key)
        if not groups:
            sections = getattr(settings, 'INDEX_SECTIONS', self.get_index_sections(request))
            groups = OrderedDict([(k, []) for k in sections.keys()])
            hiddens = sections.get('_hidden_', [])

            def get_section(model, app):
                fqn = "%s.%s" % (app['app_label'], model['object_name'])
                target = 'Other'
                if fqn in hiddens or app['app_label'] in hiddens:
                    return '_hidden_'

                for sec, models in sections.items():
                    if fqn in models:
                        return sec
                    elif app['app_label'] in models:
                        target = sec
                return target

            for app in app_list:
                for model in app['models']:
                    sec = get_section(model, app)
                    groups[sec].append(
                        {'app_label': str(app['app_label']),
                         'app_name': str(app['name']),
                         'app_url': app['app_url'],
                         'label': "%s - %s" % (app['name'], model['object_name']),
                         'model_name': str(model['name']),
                         'admin_url': model['admin_url'],
                         'perms': model['perms']})
            for __, models in groups.items():
                models.sort(key=lambda x: x['label'])
            cache.set(key, groups, 60 * 60)

        context = {
            **self.each_context(request),
            # 'title': self.index_title,
            'app_list': app_list,
            'groups': dict(groups),
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, 'admin/index_new.html', context)


class AdminConfig(SimpleAdminConfig):
    default_site = 'unicef_geospatial.config.admin.AdminSite'

    def ready(self):
        super().ready()
        self.module.autodiscover()
