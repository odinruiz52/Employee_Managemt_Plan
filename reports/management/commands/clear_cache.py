"""
Management command to clear application cache.
This is useful when you need to force refresh of cached data.
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Clear application cache'

    def add_arguments(self, parser):
        parser.add_argument(
            '--key',
            type=str,
            help='Clear specific cache key instead of all cache',
        )
        parser.add_argument(
            '--pattern',
            type=str,
            help='Clear cache keys matching pattern (e.g., "department_*")',
        )

    def handle(self, *args, **options):
        key = options.get('key')
        pattern = options.get('pattern')

        if key:
            # Clear specific key
            if cache.delete(key):
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully cleared cache key: {key}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Cache key not found: {key}')
                )
        elif pattern:
            # Clear keys matching pattern (requires more advanced cache backend)
            self.stdout.write(
                self.style.WARNING(
                    'Pattern matching requires Redis or Memcached backend. '
                    'Using clear all for local memory cache.'
                )
            )
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('Cache cleared successfully')
            )
        else:
            # Clear all cache
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('All cache cleared successfully')
            )

        # Also clear specific dashboard cache keys
        dashboard_keys = [
            'department_employee_counts',
            'attendance_by_month',
        ]
        
        for cache_key in dashboard_keys:
            cache.delete(cache_key)
            
        self.stdout.write(
            self.style.SUCCESS('Dashboard cache keys cleared')
        )