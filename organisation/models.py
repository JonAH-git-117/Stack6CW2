# from django.db import models
# from django.conf import settings

# # Create your models here.
# class Organisation(models.Model):
#     organisation_name = models.CharField(max_length=100)
#     organisation_description = models.TextField()

#     def __str__(self):
#         return self.organisation_name
    

# class Department(models.Model):
#     department_name = models.CharField(max_length=100)
#     department_description = models.TextField()
#     department_location = models.CharField(max_length=100, blank=True, null=True)

#     organisation = models.ForeignKey(
#         Organisation,
#         on_delete=models.CASCADE,
#         related_name="departments"
#     )

#     dept_head = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="headed_departments"
#     )

#     def __str__(self):
#         return self.department_name