from django.db import models

# Create your models here.


class ReadAloud(models.Model):
    sentence = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sentence[:50]  # Show first 50 characters for better readability


class ShortAnswer(models.Model):
    answer = models.TextField()  # Field to store the short answer text
    audio = models.FileField(upload_to='audio/', null=True, blank=True)  # Field to store the audio file

    def __str__(self):
        return self.answer[:50]


class SummarizePassage(models.Model):
    passage = models.TextField()
    keywords = models.TextField()

    def __str__(self):
        return f"Passage {self.id}"


class ReadMCQSingle(models.Model):
    passage = models.TextField()
    question = models.TextField()
    choice1 = models.CharField(max_length=255)
    choice2 = models.CharField(max_length=255)
    choice3 = models.CharField(max_length=255)
    choice4 = models.CharField(max_length=255)
    choice5 = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return self.question


class ReadMCQMultiple(models.Model):
    passage = models.TextField()
    question = models.TextField()
    choice1 = models.CharField(max_length=255)
    choice2 = models.CharField(max_length=255)
    choice3 = models.CharField(max_length=255)
    choice4 = models.CharField(max_length=255)
    choice5 = models.CharField(max_length=255)
    answer1 = models.CharField(max_length=255)
    answer2 = models.CharField(max_length=255)
    answer3 = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.question


class ListeningMCQSingle(models.Model):
    audio = models.FileField(upload_to='audios/')
    question = models.CharField(max_length=255)
    choice1 = models.CharField(max_length=255)
    choice2 = models.CharField(max_length=255)
    choice3 = models.CharField(max_length=255)
    choice4 = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Question with Answer: {self.answer}"


class ListeningCorrectSummary(models.Model):
    audio = models.FileField(upload_to='audios1/')
    choice1 = models.CharField(max_length=255)
    choice2 = models.CharField(max_length=255)
    choice3 = models.CharField(max_length=255)
    choice4 = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return f"Question with Answer: {self.answer}"


class ListeningFillBlanks(models.Model):
    audio = models.FileField(upload_to='audios2/')
    passage = models.TextField() # Use [[blank1]], [[blank2]], etc.
    answers = models.JSONField() # Store answers as key-value pairs

    def __str__(self):
        return self.passage[:50]
