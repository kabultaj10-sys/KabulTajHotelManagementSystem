from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create default user accounts for each role: admin, receptionist, restaurant"

    def add_arguments(self, parser):
        parser.add_argument(
            "--admin-username",
            default="Ahmad",
            help="Username for the admin account",
        )
        parser.add_argument(
            "--admin-password",
            default="admin123",
            help="Password for the admin account",
        )
        parser.add_argument(
            "--reception-username",
            default="ahmadR",
            help="Username for the receptionist account",
        )
        parser.add_argument(
            "--reception-password",
            default="admin123",
            help="Password for the receptionist account",
        )
        parser.add_argument(
            "--restaurant-username",
            default="ahmadRes",
            help="Username for the restaurant account",
        )
        parser.add_argument(
            "--restaurant-password",
            default="admin123",
            help="Password for the restaurant account",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        admin_username = options["admin_username"]
        admin_password = options["admin_password"]
        reception_username = options["reception_username"]
        reception_password = options["reception_password"]
        restaurant_username = options["restaurant_username"]
        restaurant_password = options["restaurant_password"]

        # Admin (superuser)
        admin_user, created_admin = User.objects.get_or_create(
            username=admin_username,
            defaults={
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        # Always (re)set password to ensure consistency
        admin_user.set_password(admin_password)
        admin_user.save()
        if created_admin:
            self.stdout.write(self.style.SUCCESS(f"Created admin user '{admin_username}'"))
        else:
            self.stdout.write(self.style.WARNING(f"Admin user '{admin_username}' already existed; password reset"))

        # Receptionist
        reception_user, created_reception = User.objects.get_or_create(
            username=reception_username,
            defaults={
                "email": "reception@example.com",
                "first_name": "Front",
                "last_name": "Desk",
                "role": "receptionist",
                "is_staff": True,
                "is_superuser": False,
                "is_active": True,
            },
        )
        reception_user.set_password(reception_password)
        reception_user.save()
        if created_reception:
            self.stdout.write(self.style.SUCCESS(f"Created receptionist user '{reception_username}'"))
        else:
            self.stdout.write(self.style.WARNING(f"Receptionist user '{reception_username}' already existed; password reset"))

        # Restaurant
        restaurant_user, created_restaurant = User.objects.get_or_create(
            username=restaurant_username,
            defaults={
                "email": "restaurant@example.com",
                "first_name": "Restaurant",
                "last_name": "Manager",
                "role": "restaurant",
                "is_staff": True,
                "is_superuser": False,
                "is_active": True,
            },
        )
        restaurant_user.set_password(restaurant_password)
        restaurant_user.save()
        if created_restaurant:
            self.stdout.write(self.style.SUCCESS(f"Created restaurant user '{restaurant_username}'"))
        else:
            self.stdout.write(self.style.WARNING(f"Restaurant user '{restaurant_username}' already existed; password reset"))

        self.stdout.write(self.style.SUCCESS("Seeding complete."))


