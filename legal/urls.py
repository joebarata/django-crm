from django.urls import path

from . import views


app_name = 'legal'

urlpatterns = [
    path('dashboard/', views.LegalDashboardView.as_view(), name='dashboard'),
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
    path('cases/', views.LegalCaseListView.as_view(), name='case_list'),
    path('cases/add/', views.LegalCaseCreateView.as_view(), name='case_add'),
    path('cases/<int:pk>/', views.LegalCaseDetailView.as_view(), name='case_detail'),
    path('cases/<int:pk>/edit/', views.LegalCaseUpdateView.as_view(), name='case_edit'),
    path('cases/<int:case_id>/timeline/add/', views.CaseTimelineEntryCreateView.as_view(), name='timeline_add'),
    path('cases/<int:case_id>/deadlines/add/', views.CaseDeadlineCreateView.as_view(), name='deadline_add'),
    path('cases/<int:case_id>/documents/add/', views.LegalDocumentCreateView.as_view(), name='document_add'),
    path('cases/<int:case_id>/insights/add/', views.CaseInsightCreateView.as_view(), name='insight_add'),
    path('cases/<int:case_id>/automation/add/', views.CaseAutomationRuleCreateView.as_view(), name='automation_add'),
    path('cases/<int:case_id>/access/add/', views.CaseAccessControlCreateView.as_view(), name='access_add'),
    path('calendar/', views.DeadlineCalendarView.as_view(), name='calendar'),
    path('finance/agreements/', views.FeeAgreementListView.as_view(), name='fee_agreement_list'),
    path('finance/agreements/add/', views.FeeAgreementCreateView.as_view(), name='fee_agreement_add'),
    path('finance/agreements/<int:pk>/edit/', views.FeeAgreementUpdateView.as_view(), name='fee_agreement_edit'),
]
