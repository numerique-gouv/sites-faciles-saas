from django.contrib import admin

from instances.models import EmailConfig, Instance

admin.site.register(Instance)
admin.site.register(EmailConfig)
