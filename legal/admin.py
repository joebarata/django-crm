from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from . import models


class PaymentScheduleInline(admin.TabularInline):
    model = models.PaymentSchedule
    extra = 0


class CaseTimelineInline(admin.TabularInline):
    model = models.CaseTimelineEntry
    extra = 0
    fields = ('entry_type', 'occurred_at', 'summary', 'external_reference')
    readonly_fields = ('created_by',)


class CaseDeadlineInline(admin.TabularInline):
    model = models.CaseDeadline
    extra = 0


class LegalDocumentInline(admin.TabularInline):
    model = models.LegalDocument
    extra = 0
    fields = ('title', 'document_type', 'file', 'version', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(models.ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'person_type',
        'status',
        'primary_email',
        'primary_phone',
        'area_of_practice',
    )
    list_filter = ('person_type', 'status')
    search_fields = ('display_name', 'primary_email', 'document_number')


@admin.register(models.LegalCase)
class LegalCaseAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'number',
        'court',
        'status',
        'opened_at',
        'responsible_attorney',
    )
    list_filter = ('status', 'matter_type', 'court')
    search_fields = ('title', 'number', 'subject', 'clients__display_name')
    filter_horizontal = ('clients', 'support_team')
    inlines = [CaseTimelineInline, CaseDeadlineInline, LegalDocumentInline]


@admin.register(models.FeeAgreement)
class FeeAgreementAdmin(admin.ModelAdmin):
    list_display = (
        'contract_number',
        'case',
        'client',
        'fee_type',
        'total_value',
        'status',
    )
    list_filter = ('fee_type', 'status')
    search_fields = ('contract_number', 'case__title', 'client__display_name')
    inlines = [PaymentScheduleInline]


@admin.register(models.CaseDeadline)
class CaseDeadlineAdmin(admin.ModelAdmin):
    list_display = ('case', 'title', 'due_date', 'status', 'is_critical', 'is_overdue')
    list_filter = ('status', 'is_critical')
    search_fields = ('case__title', 'title')


@admin.register(models.CaseTimelineEntry)
class CaseTimelineEntryAdmin(admin.ModelAdmin):
    list_display = ('case', 'entry_type', 'occurred_at', 'summary', 'external_reference')
    list_filter = ('entry_type',)
    search_fields = ('case__title', 'summary', 'external_reference')


@admin.register(models.LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ('case', 'title', 'document_type', 'version', 'uploaded_at', 'uploaded_by')
    list_filter = ('document_type',)
    search_fields = ('case__title', 'title')


@admin.register(models.CaseAutomationRule)
class CaseAutomationRuleAdmin(admin.ModelAdmin):
    list_display = ('case', 'name', 'trigger', 'action', 'active')
    list_filter = ('active',)
    search_fields = ('name', 'trigger', 'action')


@admin.register(models.CaseInsight)
class CaseInsightAdmin(admin.ModelAdmin):
    list_display = ('case', 'captured_at', 'win_probability', 'average_duration_days', 'revenue_forecast')
    list_filter = ('captured_at',)
    search_fields = ('case__title',)


@admin.register(models.CaseAccessControl)
class CaseAccessControlAdmin(admin.ModelAdmin):
    list_display = ('case', 'user', 'role', 'expires_at')
    list_filter = ('role',)
    search_fields = ('case__title', 'user__username', 'user__email')


@admin.register(models.AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('case', 'actor', 'action', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('case__title', 'action', 'metadata')


@admin.register(models.IntegrationSource)
class IntegrationSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'endpoint', 'active', 'last_synced_at')
    list_filter = ('source_type', 'active')
    search_fields = ('name', 'endpoint')


@admin.register(models.IntegrationEvent)
class IntegrationEventAdmin(admin.ModelAdmin):
    list_display = ('source', 'case', 'external_reference', 'occurred_at', 'processed')
    list_filter = ('processed', 'source__source_type')
    search_fields = ('external_reference', 'case__title')


@admin.register(models.PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ('agreement', 'due_date', 'amount', 'status', 'received_at')
    list_filter = ('status',)
    search_fields = ('agreement__contract_number',)


admin.site.site_header = _('Legal CRM administration')
admin.site.site_title = _('Legal CRM admin')
