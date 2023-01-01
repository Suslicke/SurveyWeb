from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.survey.index, name='index'),
    path('login/', views.auth.login, name="login"),
    path('signup/', views.auth.signup, name="signup"),
    path('surveys/', views.survey.survey_list, name='survey-list'),
    path("surveys/<int:pk>/", views.survey.detail, name="survey-detail"),
    path("surveys/create/", views.survey.create, name="survey-create"),
    path("surveys/<int:pk>/delete/", views.survey.delete, name="survey-delete"),
    path("surveys/<int:pk>/question/", views.survey.question_create, name="survey-question-create"),
    path("surveys/<int:survey_pk>/question/<int:question_pk>/delete/", views.survey.question_delete, name="question-delete"),
    path("surveys/<int:survey_pk>/question/<int:question_pk>/edit/", views.survey.question_edit, name="question-edit"),
    path("surveys/<int:survey_pk>/question/<int:question_pk>/option/", views.survey.option_create, name="survey-option-create"),
    path("surveys/<int:survey_pk>/question/<int:question_pk>/option/<int:option_pk>/delete/", views.survey.option_delete, name="option-delete"),
    path("surveys/<int:survey_pk>/question/<int:question_pk>/option/<int:option_pk>/change-correct/", views.survey.option_correct_change, name="option-correct-change"),
    path("surveys/<int:pk>/edit/", views.survey.edit, name="survey-edit"),
    path("surveys/<int:pk>/disabled", views.survey.disabled, name="survey-disabled"),
    
    path("surveys/<int:pk>/submit/", views.survey.submit, name="survey-submit"),
    path("submissions/<int:pk>/result/", views.survey.submission_result, name="submission-result"),
    # path("surveys/<int:survey_pk>/submit/", views.survey.submit, name="survey-submit"),
]
