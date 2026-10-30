from django.contrib import admin

from .models import (
    Choice,
    Course,
    Instructor,
    Learner,
    Lesson,
    Question,
    Submission,
)


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "pub_date", "lesson_count", "question_count")
    search_fields = ("name", "description")
    inlines = (LessonInline, QuestionInline)

    @admin.display(description="Lessons")
    def lesson_count(self, obj):
        return obj.lesson_set.count()

    @admin.display(description="Questions")
    def question_count(self, obj):
        return obj.question_set.count()


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("user",)


@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    list_display = ("user",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    list_filter = ("course",)
    search_fields = ("title", "content", "course__name")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "course", "grade")
    list_filter = ("course",)
    search_fields = ("question_text", "course__name")
    inlines = (ChoiceInline,)


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("choice_text", "question", "is_correct")
    list_filter = ("is_correct", "question__course")
    search_fields = ("choice_text", "question__question_text")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "created_at")
    list_filter = ("created_at", "enrollment__course")
    readonly_fields = ("created_at",)
