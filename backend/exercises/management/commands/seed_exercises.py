# Placeholder - full implementation in Phase 4
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed the exercise database with initial exercises"

    def handle(self, *args, **options):
        self.stdout.write("Seed command placeholder - implement in Phase 4")
