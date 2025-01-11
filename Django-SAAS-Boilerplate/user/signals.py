from django.dispatch import receiver
from django.db.models.signals import pre_save

from .models import User


@receiver(pre_save, sender=User)
def save_name(sender, instance, *args, **kwargs):

    name, domain = instance.email.split('@')
    
    if not instance.name:
        instance.name = name.replace('.', ' ').strip().capitalize()[:25] #eg: paul@email.com -> Paul

from django.db.models.signals import post_save 
from stocks.models import Watchlist 
import time  # For adding delay between retries

@receiver(post_save, sender=User)
def create_default_watchlist(sender, instance, created, **kwargs):
    if created:  
        retry_attempts = 3  # Max number of retries
        attempt = 0
        while attempt < retry_attempts:
            try:
                next_id = Watchlist.objects.latest('id').id + 1
                 
                while Watchlist.objects.filter(id=next_id).exists():
                    next_id += 1   
                 
                watchlist = Watchlist(id=next_id, name="Watchlist", user=instance)
                 
                watchlist.save()
                
                break

            except Exception as e: 
                print(f"Attempt {attempt + 1} failed: {e}")
                attempt += 1
                if attempt < retry_attempts:
                    print("Retrying...")
                    time.sleep(2)  
                else:
                    print("Max retry attempts reached. Watchlist creation failed.") 
