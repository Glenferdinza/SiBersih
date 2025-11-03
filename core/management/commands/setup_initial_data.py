from django.core.management.base import BaseCommand
from orders.models import Service

class Command(BaseCommand):
    help = 'Setup initial data for SiBersih'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating initial services...')
        
        services_data = [
            {
                'name': 'Cuci Setrika',
                'description': 'Layanan cuci dan setrika lengkap untuk pakaian sehari-hari',
                'base_price': 8000,
                'unit': 'kg'
            },
            {
                'name': 'Dry Clean',
                'description': 'Pembersihan kering untuk pakaian khusus seperti jas dan gaun',
                'base_price': 15000,
                'unit': 'pcs'
            },
            {
                'name': 'Cuci Ekspres',
                'description': 'Layanan cuci cepat selesai dalam 24 jam',
                'base_price': 12000,
                'unit': 'kg'
            },
            {
                'name': 'Cuci Karpet',
                'description': 'Layanan pembersihan karpet dan permadani',
                'base_price': 25000,
                'unit': 'm2'
            },
            {
                'name': 'Cuci Sepatu',
                'description': 'Pembersihan sepatu dengan treatment khusus',
                'base_price': 20000,
                'unit': 'pasang'
            },
        ]
        
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created service: {service.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Service already exists: {service.name}'))
        
        self.stdout.write(self.style.SUCCESS('Initial data setup completed!'))
