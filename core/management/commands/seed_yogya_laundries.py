from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from partners.models import MitraProfile, Laundry, CODRate
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed laundry data di Yogyakarta dengan lokasi asli'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Yogyakarta laundries...')
        
        # Create COD Rates first
        self.create_cod_rates()
        
        # Create mitra users
        mitras = self.create_mitras()
        
        # Create laundries di berbagai daerah Yogyakarta
        self.create_yogya_laundries(mitras)
        
        self.stdout.write(self.style.SUCCESS('✅ Successfully seeded Yogyakarta laundry data!'))
    
    def create_cod_rates(self):
        """Create COD rate tiers"""
        cod_rates = [
            {'min': 0, 'max': 2, 'fee': 5000},
            {'min': 2.01, 'max': 5, 'fee': 8000},
            {'min': 5.01, 'max': 10, 'fee': 12000},
            {'min': 10.01, 'max': 20, 'fee': 18000},
        ]
        
        for rate in cod_rates:
            CODRate.objects.get_or_create(
                min_distance_km=Decimal(str(rate['min'])),
                max_distance_km=Decimal(str(rate['max'])),
                defaults={'fee': Decimal(str(rate['fee']))}
            )
        
        self.stdout.write('✅ COD Rates created')
    
    def create_mitras(self):
        """Create mitra accounts"""
        mitras_data = [
            {'username': 'laundry_sleman', 'name': 'Laundry Sleman Jaya', 'district': 'Sleman'},
            {'username': 'laundry_bantul', 'name': 'Fresh Clean Bantul', 'district': 'Bantul'},
            {'username': 'laundry_umbul', 'name': 'Umbulharjo Express', 'district': 'Umbulharjo'},
            {'username': 'laundry_kota', 'name': 'Kota Laundry Premium', 'district': 'Yogyakarta'},
            {'username': 'laundry_gondok', 'name': 'Gondokusuman Clean', 'district': 'Gondokusuman'},
        ]
        
        mitras = []
        for data in mitras_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': f"{data['username']}@sibersih.com",
                    'role': 'mitra',
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            
            mitra, _ = MitraProfile.objects.get_or_create(
                user=user,
                defaults={
                    'business_name': data['name'],
                    'location': f"{data['district']}, Yogyakarta",
                    'description': f'Laundry profesional di {data["district"]} dengan pengalaman 5+ tahun',
                    'operational_cost': Decimal('5000'),
                    'rating': Decimal(str(round(random.uniform(4.5, 5.0), 1))),
                    'total_orders': random.randint(100, 500),
                    'is_active': True
                }
            )
            mitras.append(mitra)
        
        self.stdout.write(f'✅ {len(mitras)} Mitra profiles created')
        return mitras
    
    def create_yogya_laundries(self, mitras):
        """Create laundries dengan koordinat asli Yogyakarta"""
        laundries_data = [
            # Sleman Area
            {
                'name': 'Clean & Fresh Laundry Sleman',
                'address': 'Jl. Kaliurang KM 5, Caturtunggal, Depok, Sleman',
                'district': 'Sleman',
                'lat': -7.754930,
                'lon': 110.377792,
                'price': 7000,
                'mitra_idx': 0
            },
            {
                'name': 'Express Wash Condongcatur',
                'address': 'Jl. Affandi, Condongcatur, Depok, Sleman',
                'district': 'Sleman',
                'lat': -7.767420,
                'lon': 110.395980,
                'price': 6500,
                'mitra_idx': 0
            },
            # Bantul Area
            {
                'name': 'Laundry Kilat Bantul',
                'address': 'Jl. Bantul No. 45, Bantul',
                'district': 'Bantul',
                'lat': -7.887830,
                'lon': 110.329550,
                'price': 6000,
                'mitra_idx': 1
            },
            {
                'name': 'Fresh Clean Laundry Sewon',
                'address': 'Jl. Parangtritis KM 7, Sewon, Bantul',
                'district': 'Bantul',
                'lat': -7.845320,
                'lon': 110.366180,
                'price': 6500,
                'mitra_idx': 1
            },
            # Umbulharjo Area
            {
                'name': 'Umbulharjo Express Laundry',
                'address': 'Jl. Veteran No. 25, Umbulharjo, Yogyakarta',
                'district': 'Umbulharjo',
                'lat': -7.819170,
                'lon': 110.393340,
                'price': 7500,
                'mitra_idx': 2
            },
            {
                'name': 'Quick Wash Glagahsari',
                'address': 'Jl. Glagahsari No. 12, Umbulharjo, Yogyakarta',
                'district': 'Umbulharjo',
                'lat': -7.808240,
                'lon': 110.381570,
                'price': 7000,
                'mitra_idx': 2
            },
            # Kota Yogyakarta (Pusat)
            {
                'name': 'Premium Laundry Malioboro',
                'address': 'Jl. Sosrowijayan No. 8, Malioboro, Yogyakarta',
                'district': 'Yogyakarta',
                'lat': -7.792580,
                'lon': 110.365650,
                'price': 8500,
                'mitra_idx': 3
            },
            {
                'name': 'Royal Clean Jetis',
                'address': 'Jl. Jetis No. 30, Yogyakarta',
                'district': 'Yogyakarta',
                'lat': -7.789540,
                'lon': 110.373110,
                'price': 8000,
                'mitra_idx': 3
            },
            # Gondokusuman Area
            {
                'name': 'Gondok Clean Laundry',
                'address': 'Jl. Kaliurang KM 4.5, Gondokusuman, Yogyakarta',
                'district': 'Gondokusuman',
                'lat': -7.766490,
                'lon': 110.380180,
                'price': 7500,
                'mitra_idx': 4
            },
            {
                'name': 'Terban Express Wash',
                'address': 'Jl. Terban No. 15, Gondokusuman, Yogyakarta',
                'district': 'Gondokusuman',
                'lat': -7.776210,
                'lon': 110.374590,
                'price': 7000,
                'mitra_idx': 4
            },
        ]
        
        for data in laundries_data:
            Laundry.objects.get_or_create(
                name=data['name'],
                defaults={
                    'mitra': mitras[data['mitra_idx']],
                    'address': data['address'],
                    'district': data['district'],
                    'city': 'Yogyakarta',
                    'latitude': Decimal(str(data['lat'])),
                    'longitude': Decimal(str(data['lon'])),
                    'price_per_kg': Decimal(str(data['price'])),
                    'min_order_kg': Decimal('2.0'),
                    'operating_hours_start': '08:00',
                    'operating_hours_end': '20:00',
                    'estimated_pickup_time': random.randint(30, 90),
                    'estimated_delivery_time': random.randint(1200, 2880),  # 20-48 jam
                    'rating': Decimal(str(round(random.uniform(4.2, 5.0), 1))),
                    'total_reviews': random.randint(50, 300),
                    'total_orders_completed': random.randint(100, 800),
                    'is_active': True,
                    'is_open_now': True,
                    'has_regular_wash': True,
                    'has_dry_clean': True,
                    'has_express': random.choice([True, False]),
                }
            )
        
        self.stdout.write(f'✅ {len(laundries_data)} Laundries created in Yogyakarta')
