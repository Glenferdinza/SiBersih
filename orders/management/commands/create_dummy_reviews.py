from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from orders.models import Order, Review
from partners.models import Laundry
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create dummy reviews for all laundries'

    def handle(self, *args, **options):
        # Sample review comments
        positive_comments = [
            "Pelayanan sangat memuaskan! Cucian bersih dan wangi. Pengambilan dan pengantaran tepat waktu. Recommended!",
            "Laundry terbaik yang pernah saya coba. Harga terjangkau, hasil maksimal. Pasti langganan disini terus!",
            "Cucian sangat bersih dan rapi. Staf ramah dan profesional. Waktu pengerjaan juga cepat.",
            "Sangat puas dengan hasilnya! Noda membandel hilang semua. Harga juga reasonable. Top!",
            "Kualitas cucian bagus sekali, wangi dan bersih. Dijemput dan diantar ke rumah. Sangat membantu!",
            "Pelayanan cepat dan hasil memuaskan. Cucian dilipat rapi. Harga kompetitif. Terima kasih!",
            "Sudah langganan beberapa kali, selalu puas. Cucian wangi tahan lama. Recommended banget!",
            "Service excellent! Cucian bersih seperti baru. Timing pickup dan delivery on time. Good job!",
            "Pertama kali coba dan langsung jatuh cinta. Hasil cucian bersih maksimal. Pasti balik lagi!",
            "Mantap! Cucian bersih, wangi, dan rapi. Harga terjangkau untuk kualitas yang didapat.",
        ]
        
        neutral_comments = [
            "Hasilnya cukup baik, tapi pengantaran agak telat dari jadwal yang dijanjikan.",
            "Cucian bersih, tapi ada beberapa yang kurang rapi lipatannya. Overall oke sih.",
            "Layanan standar, tidak ada yang istimewa tapi juga tidak mengecewakan.",
            "Harga agak mahal menurut saya, tapi hasil cucian memang bersih.",
            "Pelayanan baik, tapi waktu tunggu agak lama. Mungkin karena lagi ramai.",
        ]
        
        # Get atau create dummy users untuk reviewers
        dummy_users = []
        user_names = ['Budi Santoso', 'Siti Nurhaliza', 'Ahmad Wijaya', 'Rina Kusuma', 
                      'Dedi Firmansyah', 'Wati Suryani', 'Hendra Setiawan', 'Dewi Lestari']
        
        for name in user_names:
            username = name.lower().replace(' ', '')
            email = f"{username}@example.com"
            first_name = name.split()[0]
            last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': f"08{random.randint(1000000000, 9999999999)}",
                    'role': 'user'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {name}'))
            dummy_users.append(user)
        
        # Get all laundries
        laundries = Laundry.objects.filter(is_active=True)
        
        if not laundries:
            self.stdout.write(self.style.ERROR('No active laundries found!'))
            return
        
        total_reviews_created = 0
        
        for laundry in laundries:
            # Create 3-4 dummy reviews per laundry
            num_reviews = random.randint(3, 4)
            
            for i in range(num_reviews):
                # Random user
                user = random.choice(dummy_users)
                
                # Create/find a default service for the order
                from orders.models import Service
                service = Service.objects.filter(is_active=True).first()
                if not service:
                    service = Service.objects.create(name='Cuci Setrika', description='Service default', base_price=5000)

                # Create dummy order first (required for review)
                order = Order.objects.create(
                    user=user,
                    laundry=laundry,
                    service=service,
                    order_number=f"DUMMY-{laundry.id}-{i+1}-{random.randint(1000,9999)}",
                    weight_kg=random.choice([3, 5, 7, 10]),
                    pickup_address=f"{random.choice(['Jl. Kaliurang', 'Jl. Malioboro', 'Jl. Gejayan', 'Jl. Magelang'])} No.{random.randint(1, 100)}",
                    pickup_time=timezone.now() - timedelta(days=random.randint(5, 30)),
                    delivery_address=f"{random.choice(['Jl. Kaliurang', 'Jl. Malioboro', 'Jl. Gejayan', 'Jl. Magelang'])} No.{random.randint(1, 100)}",
                    payment_method='cod',
                    status='delivered',
                    total_price=random.randint(15000, 60000),
                )
                
                # 80% positive reviews, 20% neutral
                is_positive = random.random() < 0.8
                
                if is_positive:
                    rating = random.choice([4, 5, 5, 5])  # Bias towards 5 stars
                    comment = random.choice(positive_comments)
                    service_quality = random.randint(4, 5)
                    cleanliness = random.randint(4, 5)
                    speed = random.randint(4, 5)
                else:
                    rating = random.choice([3, 4])
                    comment = random.choice(neutral_comments)
                    service_quality = random.randint(3, 4)
                    cleanliness = random.randint(3, 4)
                    speed = random.randint(3, 4)
                
                # Create review
                review = Review.objects.create(
                    order=order,
                    user=user,
                    laundry=laundry,
                    rating=rating,
                    comment=comment,
                    service_quality=service_quality,
                    cleanliness=cleanliness,
                    speed=speed,
                    is_approved=True,
                    created_at=timezone.now() - timedelta(days=random.randint(1, 25))
                )
                
                total_reviews_created += 1
                self.stdout.write(f'Created review for {laundry.name} - {rating}★')
            
            # Update laundry rating
            laundry.update_rating()
            self.stdout.write(self.style.SUCCESS(
                f'✓ {laundry.name} - Rating: {laundry.rating} ({laundry.total_reviews} reviews)'
            ))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Total {total_reviews_created} dummy reviews created successfully!'
        ))
