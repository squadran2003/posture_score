from django.contrib import admin
from .models import Exercise, ExerciseCategory, UserExerciseLog
@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "target_issue", "difficulty", "is_premium")
    list_filter = ("category", "target_issue", "difficulty", "is_premium")
    search_fields = ("name", "description", "instructions")