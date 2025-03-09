from django.contrib import admin

from tasks.models import KPI, KSI, MajorActivity, Milestone, Task

admin.site.register(KPI)
admin.site.register(KSI)
admin.site.register(MajorActivity)
admin.site.register(Milestone)
admin.site.register(Task)
