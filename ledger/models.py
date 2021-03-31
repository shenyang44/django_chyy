from django.db import models
import datetime
from django.utils import timezone

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        now = timezone.now()
        return now >= self.pub_date >= now - datetime.timedelta(days=1)

class Choice(models.Model): 
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text

class Account(models.Model):
    name = models.CharField(max_length=150)
    file_no = models.CharField(unique=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.IntegerField()
    def __str__(self):
        return self.name

class Transaction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    receiver = models.ForeignKey(Account, related_name='trans_in', on_delete=models.CASCADE)
    payee = models.ForeignKey(Account, related_name='trans_out', on_delete=models.CASCADE)
    received = models.BooleanField(default=True)
    descriptions = models.TextField()
    amounts = models.TextField()
    total = models.IntegerField()
    cheque_text = models.TextField(null=True)