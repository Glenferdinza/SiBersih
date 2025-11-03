"""
Generate a new Django SECRET_KEY for production use.
Run this script and copy the output to your .env file.
"""
from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("=" * 70)
    print("COPY THIS SECRET KEY TO YOUR .env FILE:")
    print("=" * 70)
    print(f"\nSECRET_KEY={secret_key}\n")
    print("=" * 70)
    print("IMPORTANT: Keep this secret! Never commit it to Git!")
    print("=" * 70)
