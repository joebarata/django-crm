from collections import defaultdict
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import generic

from . import forms
from . import models


class LegalDashboardView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'legal/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['open_cases'] = models.LegalCase.objects.filter(
            status=models.LegalCase.CaseStatus.OPEN
        ).count()
        context['upcoming_hearings'] = models.CaseTimelineEntry.objects.filter(
            entry_type=models.CaseTimelineEntry.EntryType.HEARING,
            occurred_at__gte=timezone.now(),
        ).order_by('occurred_at')[:5]
        context['pending_deadlines'] = models.CaseDeadline.objects.filter(
            status=models.CaseDeadline.DeadlineStatus.PENDING,
            due_date__gte=timezone.now(),
        ).order_by('due_date')[:5]
        context['overdue_deadlines'] = models.CaseDeadline.objects.filter(
            status=models.CaseDeadline.DeadlineStatus.PENDING,
            due_date__lt=timezone.now(),
        )
        context['top_clients'] = models.FeeAgreement.objects.values('client__display_name').annotate(
            total=Sum('total_value')
        ).order_by('-total')[:5]
        context['win_rate'] = self._calculate_win_rate()
        context['revenue_forecast'] = models.CaseInsight.objects.aggregate(
            total=Sum('revenue_forecast')
        )['total'] or 0
        return context

    def _calculate_win_rate(self):
        total_closed = models.LegalCase.objects.filter(
            status=models.LegalCase.CaseStatus.CLOSED
        ).count()
        if not total_closed:
            return 0
        wins = models.CaseInsight.objects.filter(
            case__status=models.LegalCase.CaseStatus.CLOSED,
            win_probability__gte=50
        ).count()
        return round((wins / total_closed) * 100, 2)


class ClientListView(LoginRequiredMixin, generic.ListView):
    model = models.ClientProfile
    template_name = 'legal/client_list.html'
    context_object_name = 'clients'
    paginate_by = 25


class ClientCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.ClientProfile
    form_class = forms.ClientProfileForm
    template_name = 'legal/form.html'
    success_url = reverse_lazy('legal:client_list')


class ClientUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.ClientProfile
    form_class = forms.ClientProfileForm
    template_name = 'legal/form.html'
    success_url = reverse_lazy('legal:client_list')


class LegalCaseListView(LoginRequiredMixin, generic.ListView):
    model = models.LegalCase
    template_name = 'legal/case_list.html'
    context_object_name = 'cases'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.select_related('responsible_attorney').prefetch_related('clients')


class LegalCaseCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.LegalCase
    form_class = forms.LegalCaseForm
    template_name = 'legal/form.html'
    success_url = reverse_lazy('legal:case_list')


class LegalCaseUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.LegalCase
    form_class = forms.LegalCaseForm
    template_name = 'legal/form.html'
    success_url = reverse_lazy('legal:case_list')


class LegalCaseDetailView(LoginRequiredMixin, generic.DetailView):
    model = models.LegalCase
    template_name = 'legal/case_detail.html'
    context_object_name = 'case'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        case = self.object
        context['timeline'] = case.timeline.select_related('created_by').all()[:50]
        context['deadlines'] = case.deadlines.select_related('responsible').all()
        context['documents'] = case.documents.all()
        context['fee_agreements'] = case.fee_agreements.select_related('client').all()
        context['insights'] = case.insights.all()
        context['automation_rules'] = case.automation_rules.all()
        context['access_rules'] = case.access_rules.select_related('user').all()
        context['integration_events'] = case.integration_events.select_related('source').all()[:20]
        return context


class DeadlineCalendarView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'legal/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        start = date(now.year, now.month, 1)
        deadlines = models.CaseDeadline.objects.filter(
            due_date__month=start.month,
            due_date__year=start.year,
        ).select_related('case')
        grouped = defaultdict(list)
        for deadline in deadlines:
            grouped[deadline.due_date.date()].append(deadline)
        context['grouped_deadlines'] = dict(grouped)
        context['month'] = start.strftime('%B %Y')
        return context


class FeeAgreementListView(LoginRequiredMixin, generic.ListView):
    model = models.FeeAgreement
    template_name = 'legal/fee_agreement_list.html'
    context_object_name = 'agreements'


class FeeAgreementCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.FeeAgreement
    form_class = forms.FeeAgreementForm
    template_name = 'legal/form.html'
    success_url = reverse_lazy('legal:fee_agreement_list')

    def get_initial(self):
        initial = super().get_initial()
        case_id = self.request.GET.get('case')
        client_id = self.request.GET.get('client')
        if case_id:
            initial['case'] = models.LegalCase.objects.filter(pk=case_id).first()
        if client_id:
            initial['client'] = models.ClientProfile.objects.filter(pk=client_id).first()
        return initial


class FeeAgreementUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.FeeAgreement
    form_class = forms.FeeAgreementForm
    template_name = 'legal/form.html'
    success_url = reverse_lazy('legal:fee_agreement_list')


class LegalDocumentCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.LegalDocument
    form_class = forms.LegalDocumentForm
    template_name = 'legal/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(models.LegalCase, pk=kwargs['case_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['case'] = self.case
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['case'].queryset = models.LegalCase.objects.filter(pk=self.case.pk)
        form.fields['case'].widget = form.fields['case'].hidden_widget()
        return form

    def get_success_url(self):
        return reverse_lazy('legal:case_detail', kwargs={'pk': self.object.case_id})


class CaseTimelineEntryCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.CaseTimelineEntry
    form_class = forms.CaseTimelineEntryForm
    template_name = 'legal/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(models.LegalCase, pk=kwargs['case_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['case'] = self.case
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['case'].queryset = models.LegalCase.objects.filter(pk=self.case.pk)
        form.fields['case'].widget = form.fields['case'].hidden_widget()
        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('legal:case_detail', kwargs={'pk': self.object.case_id})


class CaseDeadlineCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.CaseDeadline
    form_class = forms.CaseDeadlineForm
    template_name = 'legal/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(models.LegalCase, pk=kwargs['case_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['case'] = self.case
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['case'].queryset = models.LegalCase.objects.filter(pk=self.case.pk)
        form.fields['case'].widget = form.fields['case'].hidden_widget()
        return form

    def get_success_url(self):
        return reverse_lazy('legal:case_detail', kwargs={'pk': self.object.case_id})


class CaseInsightCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.CaseInsight
    form_class = forms.CaseInsightForm
    template_name = 'legal/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(models.LegalCase, pk=kwargs['case_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['case'] = self.case
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['case'].queryset = models.LegalCase.objects.filter(pk=self.case.pk)
        form.fields['case'].widget = form.fields['case'].hidden_widget()
        return form

    def get_success_url(self):
        return reverse_lazy('legal:case_detail', kwargs={'pk': self.object.case_id})


class CaseAutomationRuleCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.CaseAutomationRule
    form_class = forms.CaseAutomationRuleForm
    template_name = 'legal/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(models.LegalCase, pk=kwargs['case_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['case'] = self.case
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['case'].queryset = models.LegalCase.objects.filter(pk=self.case.pk)
        form.fields['case'].widget = form.fields['case'].hidden_widget()
        return form

    def get_success_url(self):
        return reverse_lazy('legal:case_detail', kwargs={'pk': self.object.case_id})


class CaseAccessControlCreateView(LoginRequiredMixin, generic.CreateView):
    model = models.CaseAccessControl
    form_class = forms.CaseAccessControlForm
    template_name = 'legal/form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(models.LegalCase, pk=kwargs['case_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['case'] = self.case
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['case'].queryset = models.LegalCase.objects.filter(pk=self.case.pk)
        form.fields['case'].widget = form.fields['case'].hidden_widget()
        return form

    def get_success_url(self):
        return reverse_lazy('legal:case_detail', kwargs={'pk': self.object.case_id})
