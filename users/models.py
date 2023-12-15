import uuid
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from rest_framework import permissions
from django.utils.translation import gettext_lazy as _


def validate_positive(value):
    if value < 0:
        raise ValidationError(
            _('%(value)s is not positive.'),
            params={"value": value}
        )


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ('-date_joined',)

    def __str__(self):
        return self.email


# ================================================================

class Dictionary(models.Model):
    uuid = models.UUIDField(
        primary_key=False, default=uuid.uuid4, editable=False)
    dictionary_code = models.CharField(max_length=5, blank=True)
    dictionary_name_en = models.CharField(max_length=50, blank=True)
    dictionary_name_sw = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.dictionary_name_en

    class Meta:
        verbose_name = "Dictionary"
        verbose_name_plural = "Dictionaries"


class DictionaryItem(models.Model):
    uuid = models.UUIDField(
        primary_key=False, default=uuid.uuid4, editable=False)
    dictionary_item_code = models.CharField(
        max_length=5, blank=True, null=True)
    dictionary_item_name_en = models.CharField(
        max_length=50, blank=True, null=True)
    dictionary_item_name_sw = models.CharField(
        max_length=50, blank=True, null=True)
    dictionary_item_parent = models.IntegerField(blank=True, null=True)
    dictionary = models.ForeignKey(Dictionary, models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.dictionary_item_name_en

    class Meta:
        verbose_name = "Dictionary Item"
        verbose_name_plural = "Dictionary Items"


class Party(CustomUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    # Add custom fields for the customer user
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    post_code = models.CharField(max_length=20, blank=True)
    identification = models.CharField(max_length=12)
    natural_person = models.BooleanField(default=True)
    citizenship = models.CharField(max_length=30)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10)
    dob = models.DateField(max_length=8)

    class Meta:
        verbose_name = 'Party'
        verbose_name_plural = 'Parties'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class StaffUser(CustomUser):
    DEPARTMENT_CHOICES = (
        ('registry', 'Registry'),
        ('executive_secretary', 'Executive Secretary'),
        ('coordination_unit', 'Coordination Unit'),
        ('urban_planning', 'Urban Planning'),
        ('valuation', 'Valuation'),
        ('3_acre_section', '3 Acre Section'),
        ('committee', 'Committee'),
        ('lease_section', 'Lease Section'),
        ('land_title', 'Land Title'),
    )
    # Add custom fields for the staff user
    employee_id = models.CharField(max_length=30)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)

    class Meta:
        def __str__(self):
            # return f'{self.first_name} {self.last_name}'
            return self.email

    def save(self, *args, **kwargs):
        self.full_clean()

        # Save the instance
        super().save(*args, **kwargs)

# lets us explicitly set upload path and filename


def upload_to(instance, filename):
    return 'uploads/{filename}'.format(filename=filename)


class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('house', 'House'),
        ('plot', 'Plot'),
        ('foundation', 'Foundation'),
        ('school', 'School'),
        ('farm', 'Farm'),
    ]

    OWNERSHIP_TYPE_CHOICES = [
        ('cro', 'CRO'),
        ('pcro', 'PCRO'),
        ('offer_letter', 'Offer Letter'),
        ('affidativ', 'Affidativ'),
        ('shehia_letter', 'Shehia Letter'),
    ]

    id = models.UUIDField(default=uuid.uuid4,
                          primary_key=True, editable=False, db_index=True)
    zupin = models.CharField(
        max_length=12, verbose_name="Property ID", blank=True)
    property_type = models.CharField(
        max_length=50, verbose_name="Property Type", choices=PROPERTY_TYPE_CHOICES)
    ownership_type = models.CharField(
        max_length=50, verbose_name="Property Ownership", choices=OWNERSHIP_TYPE_CHOICES)
    area = models.DecimalField(
        max_digits=9, decimal_places=3, validators=[validate_positive])
    locality = models.CharField(max_length=30)
    district = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    # created_by = models.ForeignKey(StaffUser,on_delete=models.SET_NULL, related_name="created_properties")

    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ('created_at',)

    def __str__(self):
        return self.zupin


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('sale', 'Sale'),
        ('gift', 'Gift'),
        ('inheritance', 'Inheritance'),
        ('lease', 'Lease'),
    ]

    id = models.UUIDField(default=uuid.uuid4,
                          primary_key=True, editable=False, db_index=True)
    form_number = models.CharField(max_length=20, unique=True)
    registration_number = models.CharField(max_length=30, unique=True)
    property = models.OneToOneField(
        Property, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES)
    received_from = models.CharField(max_length=50)
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_positive])
    transferor = models.ManyToManyField(
        Party, related_name="transferor_applications")
    transferee = models.ManyToManyField(
        Party, related_name="transferee_applications")
    file_path = models.FileField(upload_to=upload_to, blank=True, null=True)
    # stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default='received')
    # current_stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default='received')
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_valuation_done = models.BooleanField(default=False)
    is_urp_done = models.BooleanField(default=False)
    is_acre_done = models.BooleanField(default=False)
    is_committee_done = models.BooleanField(default=False)
    is_land_records_done = models.BooleanField(default=False)
    is_document_done = models.BooleanField(default=False)
    is_signed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        StaffUser, on_delete=models.SET_NULL, blank=True, null=True, related_name="created_transactions")

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ('-created_at',)

    def __str__(self):
        return self.registration_number


class TransactionAssignment(models.Model):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="assignments")
    # assigned_to = models.ManyToManyField(
    #     StaffUser, related_name="assigned_transactions")

    # Mandatory users
    assigned_to_mandatory = models.ManyToManyField(
        StaffUser, related_name="assigned_transactions_mandatory")

    # Optional user
    assigned_to_optional = models.ForeignKey(
        StaffUser, on_delete=models.SET_NULL, blank=True, null=True, related_name="assigned_transactions_optional")

    created_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        StaffUser, on_delete=models.SET_NULL, blank=True, null=True, related_name="assigned_by_transactions")

    class Meta:
        verbose_name = 'Transaction Assignment'
        verbose_name_plural = 'Transaction Assignments'
        # unique_together = ['transaction', 'assigned_to_mandatory']

    def __str__(self):
        return self.transaction.registration_number

    # def clean(self):
    #     # Validate the number of assigned users before saving
    #     max_assigned_users = 3

    #     if self.assigned_to_mandatory.count() != 2:
    #         raise ValidationError("Exactly two mandatory users are required.")

    #     if self.assigned_to_optional and self.assigned_to_mandatory.count() + 1 > max_assigned_users:
    #         raise ValidationError(
    #             f"Only {max_assigned_users} users can be assigned to a transaction.")

    # def save(self, *args, **kwargs):
    #     self.full_clean()  # Run full validation before saving
    #     super().save(*args, **kwargs)


class Inspection(models.Model):
    transaction_assigned = models.ForeignKey(
        TransactionAssignment, on_delete=models.CASCADE, related_name="transaction_inspections")
    description = models.TextField(blank=True)
    document_file = models.FileField(
        upload_to=upload_to, blank=True, null=True)
    # image = models.ImageField(upload_to='images/', blank=True, null=True)
    inspected_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    inspected_by = models.ForeignKey(
        StaffUser, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = 'Inspection'
        verbose_name_plural = 'Inspections'

    def __str__(self):
        return self.transaction_assigned.transaction.form_number


class InspectionImage(models.Model):
    inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE,
                                   related_name='images')
    image = models.ImageField(upload_to="inspections/")

    def __str__(self):
        return f"Image for {self.inspection.transaction_assigned.transaction}"
