
from django.conf import settings
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    pub_date = models.DateField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Instructor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="instructor_profile",
    )

    class Meta:
        verbose_name_plural = "Instructors"

    def __str__(self):
        return str(self.user)


class Learner(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learner_profile",
    )

    class Meta:
        verbose_name_plural = "Learners"

    def __str__(self):
        return str(self.user)


class Lesson(models.Model):
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    AUDIT = "audit"
    HONOR = "honor"

    MODE_CHOICES = [
        (AUDIT, "Audit"),
        (HONOR, "Honor"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    mode = models.CharField(
        max_length=10,
        choices=MODE_CHOICES,
        default=AUDIT
    )
    rating = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_course_enrollment"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.course}"


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()
    grade = models.IntegerField(default=1)

    def __str__(self):
        return self.content

    def is_get_score(self, selected_ids):
        try:
            selected = {int(choice_id) for choice_id in selected_ids}
        except (TypeError, ValueError):
            return 0

        correct = set(
            self.choice_set.filter(is_correct=True)
            .values_list("id", flat=True)
        )

        if correct and selected == correct:
            return self.grade
        return 0


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.content


class Submission(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE
    )
    choices = models.ManyToManyField(Choice, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"Submission {self.id} - Enrollment {self.enrollment.id}"
