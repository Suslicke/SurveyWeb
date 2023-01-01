from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import Http404


from ..models import *
from ..forms import *

def index(request):
    return render(request, "SurveyApp/index.html")

@login_required
def survey_list(request):
    surveys = Survey.objects.filter(creator=request.user).order_by("-created_at").all()
    return render(request, "SurveyApp/survey_list.html", {"surveys": surveys})

@login_required
def create(request):
    if request.method == "POST":
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.creator = request.user
            survey.save()
            return redirect("survey-question-create", pk=survey.id)
    else:
        form = SurveyForm()

    return render(request, "SurveyApp/survey_create.html", {"form": form})

@login_required
def question_create(request, pk):
    survey = get_object_or_404(Survey, pk=pk, creator=request.user)
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            question.save()
            return redirect("survey-option-create", survey_pk=pk, question_pk=question.pk)
    else:
        form = QuestionForm()

    return render(request, "SurveyApp/survey_question_create.html", {"survey": survey, "form": form})


@login_required
def question_edit(request, survey_pk, question_pk):
    survey = get_object_or_404(Survey, pk=survey_pk, creator=request.user)
    question = get_object_or_404(Question, survey_id=survey_pk, pk=question_pk)
    if request.method == "POST":
        if request.POST['prompt'] != question.prompt:
            Question.objects.filter(pk=question_pk).update(prompt=request.POST['prompt'])
        return redirect("survey-option-create", survey_pk=survey_pk, question_pk=question_pk)
    else:
        form = QuestionForm()

    return render(request, "SurveyApp/survey_question_edit.html", {"survey": survey, "form": form, 'question': question})


@login_required
def question_delete(request, survey_pk, question_pk):
    question = get_object_or_404(Question, survey_id=survey_pk, pk=question_pk)
    if request.method == "POST":
        question.delete()

    return redirect("survey-edit", pk=survey_pk)


@login_required
def edit(request, pk):
    try:
        survey = Survey.objects.prefetch_related("question_set__option_set").get(
            pk=pk, creator=request.user, is_active=False
        )
    except Survey.DoesNotExist:
        raise Http404()

    if request.method == "POST":
        survey.is_active = True
        survey.save()
        # return redirect("survey-detail", pk=pk)
        return redirect("survey-list")
    else:
        questions = survey.question_set.all()
        return render(request, "SurveyApp/survey_edit.html", {"survey": survey, "questions": questions})


@login_required
def option_create(request, survey_pk, question_pk):
    survey = get_object_or_404(Survey, pk=survey_pk, creator=request.user)
    question = Question.objects.get(pk=question_pk)
    if request.method == "POST":
        form = OptionForm(request.POST)
        if form.is_valid():
            option = form.save(commit=False)
            option.question_id = question_pk
            option.save()
    else:
        form = OptionForm()

    options = question.option_set.all()
    return render(
        request,
        "SurveyApp/survey_option_create.html",
        {"survey": survey, "question": question, "options": options, "form": form},
    )
    
@login_required
def option_delete(request, survey_pk, question_pk, option_pk):
    option = get_object_or_404(Option, question_id=question_pk, pk=option_pk)
    if request.method == "POST":
        option.delete()

    return redirect("survey-option-create", survey_pk=survey_pk, question_pk=question_pk)

@login_required
def option_correct_change(request, survey_pk, question_pk, option_pk):
    option = get_object_or_404(Option, question_id=question_pk, pk=option_pk)
    if option.is_right:
        Option.objects.filter(pk=option_pk).update(is_right=False)
    else:
        Option.objects.filter(pk=option_pk).update(is_right=True)

    return redirect("survey-option-create", survey_pk=survey_pk, question_pk=question_pk)


@login_required
def delete(request, pk):
    survey = get_object_or_404(Survey, pk=pk, creator=request.user)
    if request.method == "POST":
        survey.delete()

    return redirect("survey-list")

@login_required
def disabled(request, pk):
    
    survey = get_object_or_404(Survey, pk=pk, is_active=True)
    if request.method == "POST":
        survey.is_active = False
        survey.save()

    return redirect("survey-list")


@login_required
def detail(request, pk):
    try:
        survey = Survey.objects.prefetch_related("question_set__option_set").get(
            pk=pk, creator=request.user, is_active=True
        )
    
    except Survey.DoesNotExist:
        raise Http404()

    questions = survey.question_set.all()

    for question in questions:
        option_pks = question.option_set.values_list("pk", flat=True)
        total_answers = Answer.objects.filter(option_id__in=option_pks).count()
        for option in question.option_set.all():
            num_answers = Answer.objects.filter(option=option).count()
            option.percent = 100.0 * num_answers / total_answers if total_answers else 0
            
    public_path = reverse("survey-submit", args=[pk])
    public_url = f"{request.scheme}://{request.get_host()}{public_path}"
    num_submissions = survey.submission_set.filter(is_complete=True).count()
    return render(
        request,
        "SurveyApp/detail.html",
        {
            "survey": survey,
            "public_url": public_url,
            "questions": questions,
            "num_submissions": num_submissions,
        },
    )
    
def render_answerform(request, survey, submission, question):
    answerform = AnswerForm(submission.pk, question.pk, options=question.option_set.all())
            
    return render(request, "SurveyApp/submit.html", {'form': answerform, 'question': question, 'survey':survey})
    
def submit(request, pk):
    
    survey = get_object_or_404(Survey, pk=pk, is_active=True)
    if request.method == "POST":
        if "submission_id" not in request.POST:
            subm = Submission.objects.create(survey=survey)
            
            question = survey.question_set.first()
            
            return render_answerform(request, survey, subm, question)
        
        else:
            subm = get_object_or_404(Submission, pk=int(request.POST['submission_id']))
            quest = get_object_or_404(Question, pk=int(request.POST['question_id']))
            # get_object_or_404(Option, pk=int(request.POST['question_id']))
            
            options = []
            answers = []
            
            for option_pk in map(int, request.POST.getlist('option')):
                option = get_object_or_404(Option, pk=option_pk)
                options.append(option)
                answer = Answer(submission=subm, question=quest, option=option, user=request.user, is_complete=True)
                answers.append(answer)
                            
            Answer.objects.bulk_create(answers)
            
            prev_question = None
            next_question = None
            for q in survey.question_set.all():
                if prev_question is not None and prev_question.pk == quest.pk:
                    next_question = q
                    break
                prev_question = q
                
            if next_question is None:
                subm.is_complete = True
                subm.save()
                return redirect('submission-result', pk=subm.pk)
            
            return render_answerform(request, survey, subm, next_question)

    return render(request, "SurveyApp/start.html", {"survey": survey})


def submission_result(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    questions = []
    for q in submission.survey.question_set.all():
        question = {'prompt': q.prompt, 'options': []}
        correct_options = []
        selected_options = []
        question_is_correct = True
        for option in q.option_set.all():
            is_checked = Answer.objects.filter(submission=submission, question=q, option=option).exists()
            is_correct = option.is_right == is_checked
            answer = {'text':option.text, 'is_right': option.is_right, 'is_checked': is_checked, 'is_correct': is_correct}
            question["options"].append(answer)
            question_is_correct = question_is_correct and is_correct

            if option.is_right:
                correct_options.append(answer['text'])
            if is_checked:
                selected_options.append(answer['text'])
        
        question["correct_options"] = correct_options
        question["selected_options"] = selected_options
        question["is_correct"] = question_is_correct
        
        
        
        questions.append(question)
    
    i = 0
    for correct in range(0, len(questions)):
        if questions[correct]['is_correct']:
            i += 1
    
    percent_correct = float((i / len(questions)) * 100)
        
    return render(request, "SurveyApp/result.html", {'questions': questions, 'submission': submission, 'survey': submission.survey, 'percent_correct': percent_correct})
    