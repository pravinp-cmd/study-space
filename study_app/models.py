from django.db import models

DAYS = [
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
]


class StudentProfile(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=60, blank=True)
    grade = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.name or self.session_key


class StudySession(models.Model):
    profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    day = models.PositiveSmallIntegerField(choices=DAYS)
    subject = models.CharField(max_length=100)
    topic = models.CharField(max_length=200)
    start_time = models.TimeField()
    end_time = models.TimeField()
    completed = models.BooleanField(default=False)

    @property
    def duration_minutes(self):
        start = self.start_time.hour * 60 + self.start_time.minute
        end = self.end_time.hour * 60 + self.end_time.minute
        return end - start

    def __str__(self):
        return f"{self.subject}: {self.topic}"


class StudyAlarm(models.Model):
    profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="alarms",
    )
    time = models.TimeField()
    label = models.CharField(max_length=100, default="Study reminder")
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.label


class DailyRating(models.Model):
    profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    day = models.DateField()
    stars = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "day"],
                name="one_rating_per_profile_per_day",
            )
        ]

class StudentNote(models.Model):
    profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    title = models.CharField(max_length=120, default="Untitled note")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title