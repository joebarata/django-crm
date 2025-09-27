from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.models import Base
from common.models import Base1


class ClientProfile(Base1):
    class Meta:
        verbose_name = _('Client profile')
        verbose_name_plural = _('Client profiles')

    class PersonType(models.TextChoices):
        INDIVIDUAL = 'individual', _('Individual')
        COMPANY = 'company', _('Company')

    class EngagementStatus(models.TextChoices):
        PROSPECT = 'prospect', _('Prospect')
        ACTIVE = 'active', _('Active')
        INACTIVE = 'inactive', _('Inactive')

    display_name = models.CharField(_('Display name'), max_length=255)
    person_type = models.CharField(
        _('Person type'),
        max_length=12,
        choices=PersonType.choices,
        default=PersonType.INDIVIDUAL,
    )
    document_number = models.CharField(
        _('Document number'),
        max_length=50,
        blank=True,
        help_text=_('CPF/CNPJ or international identifier'),
    )
    primary_email = models.EmailField(_('Primary email'), blank=True)
    primary_phone = models.CharField(_('Primary phone'), max_length=50, blank=True)
    area_of_practice = models.CharField(
        _('Practice focus'),
        max_length=150,
        blank=True,
        help_text=_('Area of law or business segment associated with the client.'),
    )
    notes = models.TextField(_('Notes'), blank=True)
    status = models.CharField(
        _('Status'),
        max_length=12,
        choices=EngagementStatus.choices,
        default=EngagementStatus.PROSPECT,
    )

    def __str__(self) -> str:
        return self.display_name


class LegalCase(Base1):
    class Meta:
        verbose_name = _('Legal case')
        verbose_name_plural = _('Legal cases')
        ordering = ['-creation_date']

    class CaseStatus(models.TextChoices):
        OPEN = 'open', _('Open')
        STAYED = 'stayed', _('Stayed')
        CLOSED = 'closed', _('Closed')
        ARCHIVED = 'archived', _('Archived')

    class MatterType(models.TextChoices):
        CIVIL = 'civil', _('Civil')
        LABOR = 'labor', _('Labor')
        TAX = 'tax', _('Tax')
        CRIMINAL = 'criminal', _('Criminal')
        CORPORATE = 'corporate', _('Corporate')
        OTHER = 'other', _('Other')

    title = models.CharField(_('Title'), max_length=255)
    number = models.CharField(_('Case number'), max_length=100, unique=True)
    court = models.CharField(_('Court'), max_length=255)
    jurisdiction = models.CharField(_('Jurisdiction / Section'), max_length=255, blank=True)
    subject = models.CharField(_('Subject'), max_length=255, blank=True)
    matter_type = models.CharField(
        _('Matter type'),
        max_length=20,
        choices=MatterType.choices,
        default=MatterType.OTHER,
    )
    description = models.TextField(_('Description'), blank=True)
    status = models.CharField(
        _('Status'),
        max_length=15,
        choices=CaseStatus.choices,
        default=CaseStatus.OPEN,
    )
    clients = models.ManyToManyField(ClientProfile, related_name='cases', verbose_name=_('Clients'))
    opposing_parties = models.TextField(_('Opposing parties'), blank=True)
    responsible_attorney = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='legal_cases_responsible',
        verbose_name=_('Responsible attorney'),
    )
    support_team = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='legal_cases_support',
        verbose_name=_('Support team'),
    )
    opened_at = models.DateField(_('Opened at'), default=timezone.now)
    closed_at = models.DateField(_('Closed at'), blank=True, null=True)
    workflow = models.TextField(_('Workflow log'), blank=True, default='')

    def __str__(self) -> str:
        return f"{self.title} ({self.number})"

    @property
    def is_open(self) -> bool:
        return self.status in {self.CaseStatus.OPEN, self.CaseStatus.STAYED}


class CaseTimelineEntry(Base):
    class Meta:
        verbose_name = _('Case timeline entry')
        verbose_name_plural = _('Case timeline entries')
        ordering = ['-occurred_at']

    class EntryType(models.TextChoices):
        HEARING = 'hearing', _('Hearing')
        DEADLINE = 'deadline', _('Deadline')
        MOTION = 'motion', _('Motion / filing')
        UPDATE = 'update', _('General update')
        NOTE = 'note', _('Internal note')
        NOTIFICATION = 'notification', _('External notification')

    case = models.ForeignKey(LegalCase, related_name='timeline', on_delete=models.CASCADE)
    entry_type = models.CharField(_('Entry type'), max_length=20, choices=EntryType.choices)
    occurred_at = models.DateTimeField(_('Occurred at'), default=timezone.now)
    summary = models.CharField(_('Summary'), max_length=255)
    description = models.TextField(_('Description'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Created by'),
    )
    external_reference = models.CharField(
        _('External reference'),
        max_length=255,
        blank=True,
        help_text=_('Identifier from court or official diary integrations.'),
    )

    def __str__(self) -> str:
        return f"{self.case}: {self.get_entry_type_display()}"


class CaseDeadline(Base):
    class Meta:
        verbose_name = _('Case deadline')
        verbose_name_plural = _('Case deadlines')
        ordering = ['due_date']

    class DeadlineStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')

    case = models.ForeignKey(LegalCase, related_name='deadlines', on_delete=models.CASCADE)
    title = models.CharField(_('Title'), max_length=255)
    due_date = models.DateTimeField(_('Due date'))
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Responsible'),
        related_name='legal_deadlines_responsible',
    )
    status = models.CharField(
        _('Status'),
        max_length=10,
        choices=DeadlineStatus.choices,
        default=DeadlineStatus.PENDING,
    )
    is_critical = models.BooleanField(_('Critical deadline'), default=False)
    remind_before = models.DurationField(
        _('Remind before'),
        default=timedelta(days=2),
        help_text=_('Offset used for automated alerts.'),
    )
    timeline_entry = models.ForeignKey(
        CaseTimelineEntry,
        related_name='linked_deadlines',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    @property
    def is_overdue(self) -> bool:
        return self.status == self.DeadlineStatus.PENDING and self.due_date < timezone.now()


class FeeAgreement(Base1):
    class Meta:
        verbose_name = _('Fee agreement')
        verbose_name_plural = _('Fee agreements')

    class FeeType(models.TextChoices):
        FIXED = 'fixed', _('Fixed fee')
        HOURLY = 'hourly', _('Hourly rate')
        SUCCESS = 'success', _('Success fee')
        SUBSCRIPTION = 'subscription', _('Subscription')

    case = models.ForeignKey(LegalCase, related_name='fee_agreements', on_delete=models.CASCADE)
    client = models.ForeignKey(ClientProfile, related_name='fee_agreements', on_delete=models.CASCADE)
    contract_number = models.CharField(_('Contract number'), max_length=100)
    fee_type = models.CharField(_('Fee type'), max_length=20, choices=FeeType.choices)
    total_value = models.DecimalField(
        _('Total value'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    hourly_rate = models.DecimalField(
        _('Hourly rate'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
    )
    signed_on = models.DateField(_('Signed on'), default=timezone.now)
    valid_until = models.DateField(_('Valid until'), blank=True, null=True)
    success_fee_percentage = models.DecimalField(
        _('Success fee percentage'),
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=[
            ('draft', _('Draft')),
            ('active', _('Active')),
            ('closed', _('Closed')),
        ],
        default='active',
    )

    def __str__(self) -> str:
        return f"{self.contract_number} - {self.case}"


class PaymentSchedule(Base):
    class Meta:
        verbose_name = _('Payment schedule entry')
        verbose_name_plural = _('Payment schedule entries')
        ordering = ['due_date']

    class PaymentStatus(models.TextChoices):
        EXPECTED = 'expected', _('Expected')
        RECEIVED = 'received', _('Received')
        OVERDUE = 'overdue', _('Overdue')
        WRITEOFF = 'writeoff', _('Write-off')

    agreement = models.ForeignKey(
        FeeAgreement,
        related_name='payment_schedule',
        on_delete=models.CASCADE,
    )
    due_date = models.DateField(_('Due date'))
    amount = models.DecimalField(
        _('Amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        _('Status'),
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.EXPECTED,
    )
    received_at = models.DateField(_('Received at'), blank=True, null=True)
    notes = models.TextField(_('Notes'), blank=True)

    def mark_received(self, received_date: timezone.datetime | None = None) -> None:
        self.status = self.PaymentStatus.RECEIVED
        self.received_at = received_date or timezone.now().date()
        self.save(update_fields=['status', 'received_at'])


class LegalDocument(Base):
    class Meta:
        verbose_name = _('Legal document')
        verbose_name_plural = _('Legal documents')
        ordering = ['-uploaded_at']

    class DocumentType(models.TextChoices):
        CONTRACT = 'contract', _('Contract')
        PLEADING = 'pleading', _('Pleading')
        EVIDENCE = 'evidence', _('Evidence')
        REPORT = 'report', _('Report')
        MEMO = 'memo', _('Memo / note')
        OTHER = 'other', _('Other')

    case = models.ForeignKey(LegalCase, related_name='documents', on_delete=models.CASCADE)
    title = models.CharField(_('Title'), max_length=255)
    document_type = models.CharField(
        _('Document type'),
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
    )
    file = models.FileField(_('File'), upload_to='legal/documents/')
    uploaded_at = models.DateTimeField(_('Uploaded at'), auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Uploaded by'),
    )
    description = models.TextField(_('Description'), blank=True)
    version = models.PositiveIntegerField(_('Version'), default=1)
    previous_version = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='next_versions',
    )

    def __str__(self) -> str:
        return f"{self.case} - {self.title} (v{self.version})"


class CaseAutomationRule(Base):
    class Meta:
        verbose_name = _('Case automation rule')
        verbose_name_plural = _('Case automation rules')

    case = models.ForeignKey(LegalCase, related_name='automation_rules', on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=150)
    trigger = models.CharField(
        _('Trigger'),
        max_length=150,
        help_text=_('Description of the automation trigger (e.g. new diary entry).'),
    )
    action = models.CharField(
        _('Action'),
        max_length=150,
        help_text=_('Action executed when the trigger occurs.'),
    )
    active = models.BooleanField(_('Active'), default=True)

    def __str__(self) -> str:
        return self.name


class CaseInsight(Base):
    class Meta:
        verbose_name = _('Case insight')
        verbose_name_plural = _('Case insights')
        ordering = ['-captured_at']

    case = models.ForeignKey(LegalCase, related_name='insights', on_delete=models.CASCADE)
    captured_at = models.DateTimeField(_('Captured at'), default=timezone.now)
    win_probability = models.DecimalField(
        _('Win probability'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    average_duration_days = models.PositiveIntegerField(_('Average duration (days)'), default=0)
    revenue_forecast = models.DecimalField(
        _('Revenue forecast'),
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    notes = models.TextField(_('Notes'), blank=True)

    def __str__(self) -> str:
        return f"Insight for {self.case} at {self.captured_at:%Y-%m-%d}"


class CaseAccessControl(Base):
    class Meta:
        verbose_name = _('Case access control')
        verbose_name_plural = _('Case access controls')
        unique_together = ('case', 'user')

    class Role(models.TextChoices):
        OWNER = 'owner', _('Owner')
        EDITOR = 'editor', _('Editor')
        VIEWER = 'viewer', _('Viewer')
        EXTERNAL = 'external', _('External collaborator')

    case = models.ForeignKey(LegalCase, related_name='access_rules', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(_('Role'), max_length=10, choices=Role.choices, default=Role.EDITOR)
    expires_at = models.DateField(_('Expires at'), blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.user} - {self.case} ({self.get_role_display()})"


class AuditLog(Base):
    class Meta:
        verbose_name = _('Audit log entry')
        verbose_name_plural = _('Audit log entries')
        ordering = ['-timestamp']

    case = models.ForeignKey(LegalCase, related_name='audit_logs', on_delete=models.CASCADE)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(_('Action'), max_length=255)
    timestamp = models.DateTimeField(_('Timestamp'), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_('IP address'), blank=True, null=True)
    metadata = models.JSONField(_('Metadata'), blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.case} - {self.action}"


class IntegrationSource(Base):
    class Meta:
        verbose_name = _('Integration source')
        verbose_name_plural = _('Integration sources')

    name = models.CharField(_('Name'), max_length=100)
    source_type = models.CharField(
        _('Source type'),
        max_length=30,
        choices=[
            ('diary', _('Official diary')),
            ('court', _('Court system')),
            ('billing', _('Billing platform')),
        ],
    )
    endpoint = models.URLField(_('Endpoint'), blank=True)
    active = models.BooleanField(_('Active'), default=True)
    last_synced_at = models.DateTimeField(_('Last synced at'), blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.get_source_type_display()})"


class IntegrationEvent(Base):
    class Meta:
        verbose_name = _('Integration event')
        verbose_name_plural = _('Integration events')
        ordering = ['-occurred_at']

    source = models.ForeignKey(IntegrationSource, related_name='events', on_delete=models.CASCADE)
    case = models.ForeignKey(
        LegalCase,
        related_name='integration_events',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    external_reference = models.CharField(_('External reference'), max_length=255, blank=True)
    occurred_at = models.DateTimeField(_('Occurred at'), default=timezone.now)
    payload = models.JSONField(_('Payload'), blank=True, null=True)
    processed = models.BooleanField(_('Processed'), default=False)

    def __str__(self) -> str:
        return f"{self.source} - {self.external_reference or self.occurred_at}"
