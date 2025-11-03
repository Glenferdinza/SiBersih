from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from partners.models import MitraProfile, Laundry
from orders.models import Service
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create dummy laundries for testing'

    def handle(self, *args, **kwargs):
        # Create dummy mitra users
        mitras_data = [
            {'username': 'mitra1', 'name': 'Laundry Express Jogja', 'lat': -7.795580, 'lon': 110.369490},
            {'username': 'mitra2', 'name': 'Cuci Kilat 24 Jam', 'lat': -7.797068, 'lon': 110.370529},
            {'username': 'mitra3', 'name': 'Fresh & Clean Laundry', 'lat': -7.783800, 'lon': 110.367200},
            {'username': 'mitra4', 'name': 'Bersih Laundry Premium', 'lat': -7.801400, 'lon': 110.364300},
            {'username': 'mitra5', 'name': 'Sparkle Wash Yogya', 'lat': -7.789000, 'lon': 110.377800},
            {'username': 'mitra6', 'name': 'Quick Laundry Service', 'lat': -7.805200, 'lon': 110.374100},
            {'username': 'mitra7', 'name': 'Super Clean Express', 'lat': -7.792300, 'lon': 110.362500},
            {'username': 'mitra8', 'name': 'Laundry King Jogja', 'lat': -7.787600, 'lon': 110.358900},
        ]

        # Create default service if doesn't exist
        service, _ = Service.objects.get_or_create(
            name='Cuci Kering Setrika',
            defaults={
                'description': 'Paket lengkap cuci, kering, dan setrika',
                'base_price': Decimal('8000'),
                'unit': 'kg',
                'is_active': True
            }
        )

        for mitra_data in mitras_data:
            # Create or get mitra user
            user, created = User.objects.get_or_create(
                username=mitra_data['username'],
                defaults={
                    'email': f"{mitra_data['username']}@sibersih.com",
                    'role': 'mitra',
                    'phone': f'08123456{random.randint(1000, 9999)}',
                    'address': f'Yogyakarta, Indonesia'
                }
            )
            
            if created:
                user.set_password('mitra123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created mitra user: {user.username}'))

            # Create or get mitra profile
            mitra_profile, _ = MitraProfile.objects.get_or_create(
                user=user,
                defaults={
                    'business_name': mitra_data['name'],
                    'location': 'Yogyakarta',
                    'description': f'Laundry profesional di Yogyakarta',
                    'operational_cost': Decimal('1000000')
                }
            )

            # Create laundry if doesn't exist
            laundry, created = Laundry.objects.get_or_create(
                mitra=mitra_profile,
                defaults={
                    'name': mitra_data['name'],
                    'address': f'Jl. Testing No. {random.randint(1, 100)}, Yogyakarta',
                    'district': 'Yogyakarta',
                    'city': 'Yogyakarta',
                    'latitude': Decimal(str(mitra_data['lat'])),
                    'longitude': Decimal(str(mitra_data['lon'])),
                    'price_per_kg': Decimal(str(random.randint(7000, 12000))),
                    'min_order_kg': Decimal('2.0'),
                    'operating_hours_start': '08:00',
                    'operating_hours_end': '20:00',
                    'estimated_pickup_time': 60,
                    'estimated_delivery_time': 1440,
                    'has_regular_wash': True,
                    'has_dry_clean': random.choice([True, False]),
                    'has_express': random.choice([True, False]),
                    'rating': Decimal('0.0'),
                    'status': random.choice(['buka', 'buka', 'buka', 'full']),  # mostly open
                    'is_active': True
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Created laundry: {laundry.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Laundry already exists: {laundry.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {len(mitras_data)} laundries!'))
        self.stdout.write(self.style.SUCCESS('Login credentials for mitras: username=mitra1-8, password=mitra123'))
