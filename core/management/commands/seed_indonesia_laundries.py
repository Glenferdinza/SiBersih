from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from partners.models import Laundry, MitraProfile
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed laundries across Indonesia'

    def handle(self, *args, **kwargs):
        # Data laundry di berbagai kota Indonesia
        laundries_data = [
            # Jakarta
            {
                'name': 'Express Laundry Jakarta Pusat',
                'address': 'Jl. Cikini Raya No. 15',
                'district': 'Menteng',
                'city': 'Jakarta Pusat',
                'latitude': -6.1944,
                'longitude': 106.8229,
                'price_per_kg': Decimal('8000'),
                'phone': '021-31904567',
                'map_link': 'https://maps.app.goo.gl/XYZ1'
            },
            {
                'name': 'Clean & Fresh Laundry Kemang',
                'address': 'Jl. Kemang Raya No. 25',
                'district': 'Kemang',
                'city': 'Jakarta Selatan',
                'latitude': -6.2615,
                'longitude': 106.8166,
                'price_per_kg': Decimal('9000'),
                'phone': '021-71906789',
                'map_link': 'https://maps.app.goo.gl/XYZ2'
            },
            
            # Surabaya
            {
                'name': 'Laundry Cepat Surabaya',
                'address': 'Jl. Raya Darmo No. 88',
                'district': 'Darmo',
                'city': 'Surabaya',
                'latitude': -7.2819,
                'longitude': 112.7289,
                'price_per_kg': Decimal('7500'),
                'phone': '031-56781234',
                'map_link': 'https://maps.app.goo.gl/XYZ3'
            },
            {
                'name': 'SBY Clean Laundry',
                'address': 'Jl. Pemuda No. 45',
                'district': 'Tegalsari',
                'city': 'Surabaya',
                'latitude': -7.2608,
                'longitude': 112.7478,
                'price_per_kg': Decimal('7000'),
                'phone': '031-53412345',
                'map_link': 'https://maps.app.goo.gl/XYZ4'
            },
            
            # Bandung
            {
                'name': 'Bandung Fresh Laundry',
                'address': 'Jl. Dago No. 120',
                'district': 'Coblong',
                'city': 'Bandung',
                'latitude': -6.8701,
                'longitude': 107.6134,
                'price_per_kg': Decimal('8500'),
                'phone': '022-87651234',
                'map_link': 'https://maps.app.goo.gl/XYZ5'
            },
            {
                'name': 'Express Wash Bandung',
                'address': 'Jl. Buah Batu No. 77',
                'district': 'Buah Batu',
                'city': 'Bandung',
                'latitude': -6.9432,
                'longitude': 107.6319,
                'price_per_kg': Decimal('7500'),
                'phone': '022-73456789',
                'map_link': 'https://maps.app.goo.gl/XYZ6'
            },
            
            # Yogyakarta (existing ones will be updated)
            {
                'name': 'Laundry Express Sleman',
                'address': 'Jl. Kaliurang KM 5.5',
                'district': 'Sleman',
                'city': 'Yogyakarta',
                'latitude': -7.7546,
                'longitude': 110.3894,
                'price_per_kg': Decimal('6500'),
                'phone': '0274-12345678',
                'map_link': 'https://maps.app.goo.gl/XYZ7'
            },
            {
                'name': 'Clean Pro Jogja',
                'address': 'Jl. Solo KM 9',
                'district': 'Kalasan',
                'city': 'Yogyakarta',
                'latitude': -7.7689,
                'longitude': 110.4635,
                'price_per_kg': Decimal('6000'),
                'phone': '0274-87654321',
                'map_link': 'https://maps.app.goo.gl/XYZ8'
            },
            
            # Semarang
            {
                'name': 'Semarang Express Laundry',
                'address': 'Jl. Pandanaran No. 55',
                'district': 'Semarang Tengah',
                'city': 'Semarang',
                'latitude': -6.9832,
                'longitude': 110.4089,
                'price_per_kg': Decimal('7000'),
                'phone': '024-35671234',
                'map_link': 'https://maps.app.goo.gl/XYZ9'
            },
            
            # Medan
            {
                'name': 'Medan Clean Laundry',
                'address': 'Jl. Gatot Subroto No. 99',
                'district': 'Medan Petisah',
                'city': 'Medan',
                'latitude': 3.5896,
                'longitude': 98.6738,
                'price_per_kg': Decimal('8000'),
                'phone': '061-78901234',
                'map_link': 'https://maps.app.goo.gl/XYZ10'
            },
            
            # Makassar
            {
                'name': 'Makassar Fresh Wash',
                'address': 'Jl. AP Pettarani No. 88',
                'district': 'Panakkukang',
                'city': 'Makassar',
                'latitude': -5.1477,
                'longitude': 119.4327,
                'price_per_kg': Decimal('7500'),
                'phone': '0411-45678901',
                'map_link': 'https://maps.app.goo.gl/XYZ11'
            },
            
            # Bali
            {
                'name': 'Bali Laundry Service',
                'address': 'Jl. Sunset Road No. 200',
                'district': 'Kuta',
                'city': 'Badung',
                'latitude': -8.7185,
                'longitude': 115.1711,
                'price_per_kg': Decimal('9000'),
                'phone': '0361-89012345',
                'map_link': 'https://maps.app.goo.gl/XYZ12'
            },
            {
                'name': 'Ubud Clean Express',
                'address': 'Jl. Raya Ubud No. 45',
                'district': 'Ubud',
                'city': 'Gianyar',
                'latitude': -8.5069,
                'longitude': 115.2625,
                'price_per_kg': Decimal('8500'),
                'phone': '0361-97123456',
                'map_link': 'https://maps.app.goo.gl/XYZ13'
            },
            
            # Palembang
            {
                'name': 'Palembang Express Wash',
                'address': 'Jl. Sudirman No. 77',
                'district': 'Ilir Timur I',
                'city': 'Palembang',
                'latitude': -2.9761,
                'longitude': 104.7754,
                'price_per_kg': Decimal('7000'),
                'phone': '0711-34567890',
                'map_link': 'https://maps.app.goo.gl/XYZ14'
            },
            
            # Malang
            {
                'name': 'Malang Fresh Laundry',
                'address': 'Jl. Ijen No. 66',
                'district': 'Klojen',
                'city': 'Malang',
                'latitude': -7.9666,
                'longitude': 112.6326,
                'price_per_kg': Decimal('6500'),
                'phone': '0341-56789012',
                'map_link': 'https://maps.app.goo.gl/XYZ15'
            },
        ]
        
        # Buat atau ambil user mitra untuk laundry
        mitra_user, created = User.objects.get_or_create(
            username='mitra_dummy',
            defaults={
                'email': 'mitra@sibersih.com',
                'first_name': 'Mitra',
                'last_name': 'Dummy',
                'phone': '081234567890',
                'address': 'Indonesia',
                'role': 'mitra',
                'is_active': True
            }
        )
        
        if created:
            mitra_user.set_password('mitra123')
            mitra_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created mitra user: {mitra_user.username}'))
        
        # Buat MitraProfile untuk user
        mitra_profile, created = MitraProfile.objects.get_or_create(
            user=mitra_user,
            defaults={
                'business_name': 'SiBersih Laundry Network',
                'location': 'Indonesia',
                'description': 'Jaringan laundry terpercaya di seluruh Indonesia',
                'operational_cost': Decimal('5000000.00'),
                'rating': Decimal('4.8'),
                'total_orders': 5000,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created mitra profile: {mitra_profile.business_name}'))
        
        # Seed laundries
        created_count = 0
        updated_count = 0
        
        for data in laundries_data:
            laundry, created = Laundry.objects.update_or_create(
                name=data['name'],
                defaults={
                    'mitra': mitra_profile,
                    'address': data['address'],
                    'district': data['district'],
                    'city': data.get('city', 'Yogyakarta'),
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                    'price_per_kg': data['price_per_kg'],
                    'min_order_kg': Decimal('2.0'),
                    'estimated_pickup_time': random.randint(30, 90),
                    'rating': round(random.uniform(4.2, 5.0), 1),
                    'total_reviews': random.randint(50, 500),
                    'total_orders_completed': random.randint(100, 1000),
                    'is_active': True,
                    'map_link': data['map_link'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {laundry.name} in {laundry.district}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'Updated: {laundry.name} in {laundry.district}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nSeeding completed!'))
        self.stdout.write(self.style.SUCCESS(f'Created: {created_count} laundries'))
        self.stdout.write(self.style.SUCCESS(f'Updated: {updated_count} laundries'))
        self.stdout.write(self.style.SUCCESS(f'Total: {created_count + updated_count} laundries'))
