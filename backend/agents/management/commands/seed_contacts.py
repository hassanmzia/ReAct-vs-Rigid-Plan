"""Seed contacts from the notebook's sample database."""

from django.core.management.base import BaseCommand
from agents.models import Contact


SEED_CONTACTS = [
    {"name": "John Smith", "email": "john.smith@example.com",
     "department": "Research & Development", "role": "Senior Engineer"},
    {"name": "John Doe", "email": "john.doe@example.com",
     "department": "Human Resources", "role": "HR Manager"},
    {"name": "Alice", "email": "alice@example.com",
     "department": "International Sales", "role": "Sales Director"},
    {"name": "Bob Wilson", "email": "bob.wilson@example.com",
     "department": "Finance", "role": "Financial Analyst"},
    {"name": "Carol Martinez", "email": "carol.martinez@example.com",
     "department": "Engineering", "role": "Tech Lead"},
    {"name": "David Chen", "email": "david.chen@example.com",
     "department": "Product Management", "role": "Product Manager"},
    {"name": "Eve Johnson", "email": "eve.johnson@example.com",
     "department": "Marketing", "role": "Marketing Director"},
    {"name": "Frank Brown", "email": "frank.brown@example.com",
     "department": "Operations", "role": "Operations Manager"},
]


class Command(BaseCommand):
    help = "Seed the contacts database with sample data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-input", action="store_true",
            help="Skip confirmation prompt",
        )

    def handle(self, *args, **options):
        if Contact.objects.exists() and not options.get("no_input"):
            self.stdout.write("Contacts already seeded, skipping.")
            return

        created = 0
        for contact_data in SEED_CONTACTS:
            _, was_created = Contact.objects.get_or_create(
                email=contact_data["email"],
                defaults=contact_data,
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} contacts."))
