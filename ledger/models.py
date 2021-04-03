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

class Client_Account(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.TextField(unique=True)
    balance = models.DecimalField(max_digits=11 ,decimal_places=2)
    
class Account(models.Model):
    name = models.CharField(max_length=150)
    file_no = models.CharField(unique=True, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.DecimalField(max_digits=11, decimal_places=2)
    client_account = models.ForeignKey(Client_Account, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.name

    def outstanding(self):
        if self.file_no.startswith('OFFICE'):
            return self.trans_out.all().filter(settled=False)
        else: 
            return "Sorry but you do not have access to this."
    
    def is_client(self):
        if self.client_account:
            return True
        else:
            return False 

class Transaction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    receiver = models.ForeignKey(Account, related_name='trans_in', on_delete=models.CASCADE)
    payee = models.ForeignKey(Account, related_name='trans_out', on_delete=models.CASCADE)
    received = models.BooleanField(default=True)
    descriptions = models.TextField()
    amounts = models.TextField()
    total = models.DecimalField(max_digits=11, decimal_places=2)
    cheque_text = models.TextField(null=True)
    settled = models.BooleanField(default=True)
