# from django.db import models

# # Create your models here.
# from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# class UserManager(BaseUserManager):
#     def create_user(self, email, name ,tc, password=None,password2=None):
#         if not email:
#             raise ValueError("Users must have an email address")

#         user = self.model(
#             email=self.normalize_email(email),
#             name=name,
#             tc=tc,
#         )
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, name,tc, password=None):
#         user = self.create_user(
#             email,
#             password=password,
#             name=name,
#             tc=tc,
#         )
#         user.is_admin = True
#         user.save(using=self._db)
#         return user
# class User(AbstractBaseUser):
#     email = models.EmailField(
#         verbose_name="Email",
#         max_length=255,
#         unique=True,
#     )
#     name = models.CharField(max_length=200)
#     tc=models.BooleanField()
#     is_active = models.BooleanField(default=True)
#     is_admin = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     objects = UserManager()

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = ['name','tc']

#     def __str__(self):
#         return self.email

#     def has_perm(self, perm, obj=None):
#         return self.is_admin

#     def has_module_perms(self, app_label):
#         return True

#     @property
#     def is_staff(self):
#         return self.is_admin

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    ROLE_RECRUITER = 'recruiter'
    ROLE_APPLICANT = 'applicant'
    ROLE_CHOICES = [(ROLE_RECRUITER,'Recruiter'),(ROLE_APPLICANT,'Applicant')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_APPLICANT)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.email})"


class JobListing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_listings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.company}"


class JobApplication(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_REVIEWED = 'Reviewed'
    STATUS_ACCEPTED = 'Accepted'
    STATUS_REJECTED = 'Rejected'
    STATUS_CHOICES = [(STATUS_PENDING,'Pending'),(STATUS_REVIEWED,'Reviewed'),(STATUS_ACCEPTED,'Accepted'),(STATUS_REJECTED,'Rejected')]

    job_listing = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    resume_link = models.URLField(null=True, blank=True)
    cover_letter = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job_listing','applicant')
        ordering = ['-applied_at']

    def __str__(self):
        return f"Application by {self.applicant.username} to {self.job_listing.title}"



