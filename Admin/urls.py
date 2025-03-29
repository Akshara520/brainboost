from django.urls import path
from .views import *

urlpatterns = [
    path('', admin_dashboard, name='admin_dashboard'),

    path('admin_registration/', admin_registration, name='admin_registration'),
    path('admin_login/', admin_login, name='admin_login'),
    path('admin_otp/', admin_otp, name='admin_otp'),
    path('admin_password_reset/', admin_password_reset, name='admin_password_reset'),
    path('admin_logout/', admin_logout, name='admin_logout'),

    #    main pages of project

    path('l_correct_summary_add/', l_correct_summary_add, name='l_correct_summary_add'),
    path('l_correct_summary_edit/<int:lcs_id>/', l_correct_summary_edit, name='l_correct_summary_edit'),
    path('l_correct_summary_show/', l_correct_summary_show, name='l_correct_summary_show'),
    path('l_correct_summary_delete/<int:lcs_id>/', l_correct_summary_delete, name='l_correct_summary_delete'),

    path('l_fill_blanks_add/', l_fill_blanks_add, name='l_fill_blanks_add'),
    path('l_fill_blanks_edit/<int:lfb_id>/', l_fill_blanks_edit, name='l_fill_blanks_edit'),
    path('l_fill_blanks_show/', l_fill_blanks_show, name='l_fill_blanks_show'),
    path('l_fill_blanks_delete/<int:lfb_id>/', l_fill_blanks_delete, name='l_fill_blanks_delete'),

    path('l_mcq_single_add/', l_mcq_single_add, name='l_mcq_single_add'),
    path('l_mcq_single_edit/<int:mcq_id>/', l_mcq_single_edit, name='l_mcq_single_edit'),
    path('l_mcq_single_show/', l_mcq_single_show, name='l_mcq_single_show'),
    path('l_mcq_single_delete/<int:mcq_id>/', l_mcq_single_delete, name='l_mcq_single_delete'),


    path('r_mcq_multiple_add/', r_mcq_multiple_add, name='r_mcq_multiple_add'),
    path('r_mcq_multiple_edit/<int:mcq_id>/', r_mcq_multiple_edit, name='r_mcq_multiple_edit'),
    path('r_mcq_multiple_show/', r_mcq_multiple_show, name='r_mcq_multiple_show'),
    path('r_mcq_multiple_delete/<int:mcq_id>/', r_mcq_multiple_delete, name='r_mcq_multiple_delete'),

    path('r_mcq_single_add/', r_mcq_single_add, name='r_mcq_single_add'),
    path('r_mcq_single_edit/<int:mcq_id>/', r_mcq_single_edit, name='r_mcq_single_edit'),
    path('r_mcq_single_show/', r_mcq_single_show, name='r_mcq_single_show'),
    path('r_mcq_single_delete/<int:mcq_id>/', r_mcq_single_delete, name='r_mcq_single_delete'),


    path('s_read_aloud_add/', s_read_aloud_add, name='s_read_aloud_add'),
    path('s_read_aloud_edit/<int:sentence_id>/', s_read_aloud_edit, name='s_read_aloud_edit'),
    path('s_read_aloud_show/', s_read_aloud_show, name='s_read_aloud_show'),
    path('s_read_aloud_delete/<int:sentence_id>/', s_read_aloud_delete, name='s_read_aloud_delete'),

    path('s_short_answer_add/', s_short_answer_add, name='s_short_answer_add'),
    path('s_short_answer_edit/<int:short_answer_id>/', s_short_answer_edit, name='s_short_answer_edit'),
    path('s_short_answer_show/', s_short_answer_show, name='s_short_answer_show'),
    path('s_short_answer_delete/<int:short_answer_id>/', s_short_answer_delete, name='s_short_answer_delete'),


    path('w_summarize_passage_add/', w_summarize_passage_add, name='w_summarize_passage_add'),
    path('w_summarize_passage_edit/<int:summarize_id>/', w_summarize_passage_edit, name='w_summarize_passage_edit'),
    path('w_summarize_passage_show/', w_summarize_passage_show, name='w_summarize_passage_show'),
    path('w_summarize_passage_delete/<int:summarize_id>/', w_summarize_passage_delete, name='w_summarize_passage_delete'),


    path('aspirant_details/', aspirant_details, name='aspirant_details'),
    path('aspirant_result/', aspirant_result_full, name='aspirant_result_full'),
    path('admin/aspirant-results/', aspirant_results_admin, name='admin_aspirant_results'),
]