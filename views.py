from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Choice, Course, Enrollment, Submission


def course_list(request):
    courses = Course.objects.all()
    return render(request, "onlinecourse/course_list_bootstrap.html", {"courses": courses})


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = None
    submission_exists = False
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        if enrollment is not None:
            submission_exists = Submission.objects.filter(enrollment=enrollment).exists()
    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {
            "course": course,
            "enrollment": enrollment,
            "submission_exists": submission_exists,
        },
    )


@login_required
@require_POST
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    Enrollment.objects.get_or_create(user=request.user, course=course)
    messages.success(request, "You are enrolled. You can now take the examination.")
    return redirect("onlinecourse:course_details", course_id=course.pk)


@login_required
@require_POST
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if enrollment is None:
        raise PermissionDenied("You must be enrolled in this course to submit an exam.")

    submitted_ids = request.POST.getlist("choice_ids")
    try:
        selected_ids = {int(choice_id) for choice_id in submitted_ids}
    except ValueError:
        return HttpResponseBadRequest("Choice IDs must be integers.")

    valid_ids = set(
        Choice.objects.filter(question__course=course, id__in=selected_ids).values_list(
            "id", flat=True
        )
    )
    if selected_ids != valid_ids:
        return HttpResponseBadRequest("One or more selected choices are invalid.")

    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(valid_ids)
    return redirect("onlinecourse:show_exam_result", course_id=course.pk)


@login_required
def show_exam_result(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if enrollment is None:
        raise PermissionDenied("You must be enrolled in this course to view exam results.")
    submission = (
        Submission.objects.filter(enrollment=enrollment)
        .prefetch_related("choices", "choices__question", "choices__question__choice_set")
        .first()
    )
    if submission is None:
        messages.info(request, "Submit the examination to view your result.")
        return redirect("onlinecourse:course_details", course_id=course.pk)

    selected_ids = set(submission.choices.values_list("id", flat=True))
    questions = []
    total_possible = 0
    score = 0
    for question in course.question_set.prefetch_related("choice_set").all():
        correct_choices = list(question.choice_set.filter(is_correct=True))
        selected_choices = [
            choice for choice in question.choice_set.all() if choice.id in selected_ids
        ]
        is_correct = question.is_get_score([choice.id for choice in selected_choices])
        total_possible += question.grade
        if is_correct:
            score += question.grade
        questions.append(
            {
                "question": question,
                "selected_choices": selected_choices,
                "correct_choices": correct_choices,
                "is_correct": is_correct,
            }
        )

    percentage = round(score / total_possible * 100, 1) if total_possible else 0
    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        {
            "course": course,
            "submission": submission,
            "questions": questions,
            "score": score,
            "total_possible": total_possible,
            "percentage": percentage,
        },
    )
