from django.contrib import admin
from .models import Exercise, ExerciseSet
@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'muscle_group')
    search_fields = ('name', 'muscle_group')