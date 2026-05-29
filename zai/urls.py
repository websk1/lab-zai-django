"""
URL configuration for zai project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from OfertaPanel import views as panel_views
from Register import views as register_views
from Issues import views as issues_views

urlpatterns = [
    path('', RedirectView.as_view(url='/offer/', permanent=False)),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('offer-mng/', include('OfertaPanel.urls')),
    path('offer/', include('OfertaPubliczna.urls')),
    path('register/', include('Register.urls')),
    path('issues/', include('Issues.urls')),
    path('categories/', panel_views.api_categories, name='api_categories'),
    path('courses/', panel_views.api_courses, name='api_courses'),
    path('registers/', register_views.api_registers, name='api_registers'),
    path('register/<int:id>/', register_views.api_register_detail, name='api_register_detail'),
    path('problemReport/', issues_views.api_problem_report, name='api_problem_report'),
    path('problems/', issues_views.api_problems, name='api_problems'),
    path('formTemplates', panel_views.api_form_templates, name='api_form_templates'),
    path('messageTemplates', panel_views.api_message_templates, name='api_message_templates'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)