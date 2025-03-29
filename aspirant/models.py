from django.db import models
from django.contrib.auth.models import User
from Admin.models import *

# Create your models here.


class AspirantReg(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reg_id = models.IntegerField(default=0)
    mobile = models.CharField(max_length=15)
    dob = models.DateField()


class ReadingMCQSingleTest(models.Model):
    student = models.CharField(max_length=255)
    reg_id = models.IntegerField()
    question = models.ForeignKey(ReadMCQSingle, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255, null=True, blank=True)


class ReadingTestResult(models.Model):
    student = models.CharField(max_length=255)
    reg_id = models.IntegerField()
    mark = models.IntegerField(default=0)


class Read_aloud_submit(models.Model):
    questions = models.ForeignKey(ReadAloud, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    mark = models.IntegerField(default=0, null=True)


class Short_answer_submit(models.Model):
    questions = models.ForeignKey(ShortAnswer, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    mark = models.IntegerField(default=0, null=True)



class SummarizePassageSubmit(models.Model):
    Summarize_question = models.ForeignKey(SummarizePassage, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    mark = models.IntegerField(default=0, null=True)


class MCQMultipleSubmit(models.Model):
    Summarize_question = models.ForeignKey(ReadMCQMultiple, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    mark = models.IntegerField(default=0, null=True)


class ListeningCorrectSummarySubmit(models.Model):
    Listening_quetion = models.ForeignKey(ListeningCorrectSummary, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    mark = models.IntegerField(default=0, null=True)



class ListeningMCQSingleSubmit(models.Model):
    Single_listen = models.ForeignKey(ListeningMCQSingle, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    mark = models.IntegerField(default=0, null=True)


class ListeningFillBlanksSubmit(models.Model):
    question_blank = models.ForeignKey(ListeningFillBlanks, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    mark = models.IntegerField(default=0, null=True)

class ResultHistory(models.Model):

    student = models.ForeignKey(User, on_delete=models.CASCADE) # Track user
    writing = models.IntegerField()
    reading = models.IntegerField()
    speaking = models.IntegerField()
    listening = models.IntegerField()
    total = models.IntegerField()
    attempted_on = models.DateTimeField(auto_now_add=True) # Store attempt time



class Final_Result(models.Model):
    speaking = models.IntegerField(null=True, blank=True, default=0)
    writing = models.IntegerField(null=True, blank=True, default=0)
    reading = models.IntegerField(null=True, blank=True, default=0)
    listening = models.IntegerField(null=True, blank=True, default=0)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="results")



    def __str__(self):
        return f"{self.student.username} - Final Result"