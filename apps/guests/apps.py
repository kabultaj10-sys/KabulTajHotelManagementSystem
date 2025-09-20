from django.apps import AppConfig


class GuestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.guests'
    verbose_name = 'Guests'

    def ready(self):
        from django.db.models.signals import post_save
        from django.dispatch import receiver
        from .models import Guest, GuestProfileSummary
        from apps.bookings.models import Booking
        from django.db.models import Sum
        from django.db.utils import OperationalError, ProgrammingError

        @receiver(post_save, sender=Guest)
        def ensure_guest_summary(sender, instance, created, **kwargs):
            # Create or update summary with aggregate data
            try:
                total_bookings = instance.bookings.count()
                completed = instance.bookings.filter(status='completed').count()
                # Sum total nights
                nights = 0
                for b in instance.bookings.all():
                    try:
                        nights += max(0, (b.check_out_date - b.check_in_date).days)
                    except Exception:
                        pass
                total_spent = instance.bookings.filter(status='completed').aggregate(
                    total=Sum('total_amount')
                )['total'] or 0

                summary, _ = GuestProfileSummary.objects.get_or_create(guest=instance)
                summary.country = instance.country or ''
                summary.city = instance.city or ''
                summary.nationality = instance.nationality or ''
                summary.total_bookings = total_bookings
                summary.completed_bookings = completed
                summary.total_nights = nights
                summary.total_spent = total_spent
                summary.save()
            except (OperationalError, ProgrammingError):
                # Table might not exist yet during initial migrations
                return

        @receiver(post_save, sender=Booking)
        def update_guest_summary_on_booking(sender, instance, **kwargs):
            guest = instance.guest
            if not guest:
                return
            try:
                total_bookings = guest.bookings.count()
                completed = guest.bookings.filter(status='completed').count()
                nights = 0
                for b in guest.bookings.all():
                    try:
                        nights += max(0, (b.check_out_date - b.check_in_date).days)
                    except Exception:
                        pass
                total_spent = guest.bookings.filter(status='completed').aggregate(
                    total=Sum('total_amount')
                )['total'] or 0

                summary, _ = GuestProfileSummary.objects.get_or_create(guest=guest)
                summary.total_bookings = total_bookings
                summary.completed_bookings = completed
                summary.total_nights = nights
                summary.total_spent = total_spent
                summary.save()
            except (OperationalError, ProgrammingError):
                return
