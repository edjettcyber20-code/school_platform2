from django.contrib import admin
from .models import (Level, Subject, Classroom, Enrollment, Schedule,
                     Assignment, Grade, Attendance, Announcement,
                     Trimester, SubjectGrade, ReportCard)

admin.site.register(Level)
admin.site.register(Subject)
admin.site.register(Classroom)
admin.site.register(Enrollment)
admin.site.register(Schedule)
admin.site.register(Assignment)
admin.site.register(Grade)
admin.site.register(Attendance)
admin.site.register(Announcement)


@admin.register(Trimester)
class TrimesterAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'school_year', 'number', 'start_date', 'end_date', 'is_active']


@admin.register(SubjectGrade)
class SubjectGradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'classroom', 'trimester', 'average', 'weighted_average']
    list_filter  = ['trimester', 'classroom']


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = ['student', 'classroom', 'trimester', 'general_average', 'rank', 'status']
    list_filter  = ['trimester', 'classroom', 'status']
