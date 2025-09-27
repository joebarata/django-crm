from django import forms
from django.utils.translation import gettext_lazy as _

from . import models


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = field.widget.attrs.get('class', '')
            if not isinstance(field.widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple, forms.RadioSelect)):
                field.widget.attrs['class'] = f"{css_class} form-control".strip()
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = f"{css_class} form-check".strip()


class ClientProfileForm(BootstrapModelForm):
    class Meta:
        model = models.ClientProfile
        fields = [
            'display_name',
            'person_type',
            'document_number',
            'primary_email',
            'primary_phone',
            'area_of_practice',
            'status',
            'notes',
            'department',
            'owner',
        ]


class LegalCaseForm(BootstrapModelForm):
    class Meta:
        model = models.LegalCase
        fields = [
            'title',
            'number',
            'court',
            'jurisdiction',
            'subject',
            'matter_type',
            'description',
            'status',
            'clients',
            'opposing_parties',
            'responsible_attorney',
            'support_team',
            'opened_at',
            'closed_at',
            'department',
            'owner',
        ]
        widgets = {
            'clients': forms.CheckboxSelectMultiple,
            'support_team': forms.CheckboxSelectMultiple,
            'opened_at': forms.DateInput(attrs={'type': 'date'}),
            'closed_at': forms.DateInput(attrs={'type': 'date'}),
        }


class CaseDeadlineForm(BootstrapModelForm):
    class Meta:
        model = models.CaseDeadline
        fields = [
            'case',
            'title',
            'due_date',
            'responsible',
            'status',
            'is_critical',
            'remind_before',
        ]
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class FeeAgreementForm(BootstrapModelForm):
    class Meta:
        model = models.FeeAgreement
        fields = [
            'case',
            'client',
            'contract_number',
            'fee_type',
            'total_value',
            'hourly_rate',
            'signed_on',
            'valid_until',
            'success_fee_percentage',
            'status',
            'department',
            'owner',
        ]
        widgets = {
            'signed_on': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
        }


class LegalDocumentForm(BootstrapModelForm):
    class Meta:
        model = models.LegalDocument
        fields = [
            'case',
            'title',
            'document_type',
            'file',
            'description',
            'version',
            'previous_version',
        ]


class CaseTimelineEntryForm(BootstrapModelForm):
    class Meta:
        model = models.CaseTimelineEntry
        fields = [
            'case',
            'entry_type',
            'occurred_at',
            'summary',
            'description',
            'external_reference',
        ]
        widgets = {
            'occurred_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CaseInsightForm(BootstrapModelForm):
    class Meta:
        model = models.CaseInsight
        fields = [
            'case',
            'captured_at',
            'win_probability',
            'average_duration_days',
            'revenue_forecast',
            'notes',
        ]
        widgets = {
            'captured_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CaseAutomationRuleForm(BootstrapModelForm):
    class Meta:
        model = models.CaseAutomationRule
        fields = ['case', 'name', 'trigger', 'action', 'active']


class CaseAccessControlForm(BootstrapModelForm):
    class Meta:
        model = models.CaseAccessControl
        fields = ['case', 'user', 'role', 'expires_at']
        widgets = {
            'expires_at': forms.DateInput(attrs={'type': 'date'}),
        }
