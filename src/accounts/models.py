import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        COMPANY = "company", "Company"
        INSTITUTION = "institution", "Institution"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.STUDENT)
    is_verified = models.BooleanField(default=False)


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    institution = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="institution_students",
        limit_choices_to={"role": User.Role.INSTITUTION},
    )
    filiere = models.CharField(max_length=128, blank=True)
    level = models.CharField(max_length=64, blank=True)
    academic_year = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Profil étudiant {self.user.email}"


class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company_profile")
    organisation_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    country_code = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    duns = models.CharField(max_length=64, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Profil entreprise {self.organisation_name or self.user.email}"


class InstitutionProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="institution_profile")
    organisation_name = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    country_code = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="institution_logos/", blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Profil établissement {self.organisation_name or self.user.email}"


class StudentInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        SENT = "sent", "Envoyée"
        FAILED = "failed", "Erreur"
        USED = "used", "Utilisée"
        EXPIRED = "expired", "Expirée"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
        limit_choices_to={"role": User.Role.INSTITUTION},
    )
    email = models.EmailField()
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    filiere = models.CharField(max_length=128)
    level = models.CharField(max_length=64)
    academic_year = models.CharField(max_length=32)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    used_at = models.DateTimeField(null=True, blank=True)
    error_message = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["token"]),
            models.Index(fields=["email", "institution"]),
        ]

    def mark_sent(self) -> None:
        self.status = self.Status.SENT
        self.sent_at = timezone.now()
        self.error_message = ""
        self.save(update_fields=["status", "sent_at", "error_message"])

    def mark_failed(self, message: str) -> None:
        self.status = self.Status.FAILED
        self.error_message = message[:250]
        self.save(update_fields=["status", "error_message"])

    def mark_used(self) -> None:
        self.status = self.Status.USED
        self.used_at = timezone.now()
        self.save(update_fields=["status", "used_at"])


class Offer(models.Model):
    class ContractType(models.TextChoices):
        STAGE = "stage", "Stage"
        ALTERNANCE = "alternance", "Alternance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=255)
    salary = models.CharField(max_length=100, blank=True)
    contract_type = models.CharField(max_length=20, choices=ContractType.choices, default=ContractType.STAGE)
    location = models.CharField(max_length=255)
    skills = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=64, blank=True)
    remote = models.BooleanField(default=False)
    start_date = models.CharField(max_length=50, blank=True)
    duration = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title
