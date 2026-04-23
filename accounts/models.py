from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    # OneToOneField links each Profile to exactly one User 
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # These three fields are identical to the lecture
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=30, blank=True)

    # Lecture uses ForeignKey('Team') as a local reference since Team is in the same app
    team = models.ForeignKey(
        # 'teams.Team' instead to reference Team across apps (cross-app reference)
        'teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        # blank=True alongside null=True so Django forms allow this field to be empty
        blank=True
    )

    def __str__(self):
        return self.user.username

# Signal identical to lecture — automatically creates a Profile when a new User registers
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Signal identical to lecture — automatically saves the Profile whenever the User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()