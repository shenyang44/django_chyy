from django.core.validators import MinValueValidator
from django.db import models
import datetime
from django.utils import timezone
import json

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
    bank_name = models.CharField(max_length=120)
    acc_number = models.CharField(max_length=60)
    bank_code = models.CharField(max_length=30)
    
class Account(models.Model):
    name = models.CharField(max_length=100)
    file_no = models.CharField(unique=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    balance = models.DecimalField(max_digits=11, decimal_places=2)
    client_code = models.CharField(max_length=20, null=True)
    client_account = models.BooleanField(default=False)
    subject_matter = models.TextField(null=True)
    subj_list = models.TextField(null=True)
    opening_date = models.DateField(null=True)
    closing_date = models.DateField(null=True)
    closing_no = models.TextField(null=True)
    other_list = models.TextField(null=True)

    def __str__(self):
        return self.name

    def outstanding(self):
        if self.file_no.startswith('OFFICE'):
            return self.trans_out.all().filter(settled=False)
        else: 
            return "Sorry but you do not have access to this."
    
    def is_external(self):
        if self.file_no.startswith('EXTERNAL'):
            return True
        else: 
            return False
    
    def is_office(self):
        if self.file_no.startswith('OFFICE'):
            return True
        else:
            return False

class Transaction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    receiver = models.ForeignKey(Account, related_name='trans_in', on_delete=models.CASCADE)
    payee = models.ForeignKey(Account, related_name='trans_out', on_delete=models.CASCADE)
    table_list = models.TextField()
    total = models.DecimalField(max_digits=11, decimal_places=2)
    cheque_text = models.TextField(null=True)
    resolved = models.BooleanField(default=True)
    cleared = models.BooleanField(default=True)
    category = models.CharField(max_length=2)
    cli_acc = models.ForeignKey(Client_Account, related_name='transactions', on_delete=models.CASCADE, null=True)
    ad_link = models.ForeignKey('self', related_name='cli_ad_link', null=True, on_delete=models.CASCADE)
    checked = models.BooleanField(default=False)
    subj_matter = models.TextField(null=True)
    voucher_no = models.IntegerField(null=True, unique=True,)
    receipt_no = models.IntegerField(null=True, unique=True,)
    off_voucher_no = models.IntegerField(null=True, unique=True,)
    voucher_ref = models.TextField(null=True)
    receipt_ref = models.TextField(null=True)

    def __str__(self):
        entries = json.loads(self.table_list)
        return(entries[0]['description'])
    
    def next_voucher_no(self):
        latest = Transaction.objects.filter(voucher_no__isnull=False).order_by('-voucher_no')[0]
        if latest:
            return (latest.voucher_no + 1)
        else:
            return 43001

    def next_receipt_no(self):
        latest = Transaction.objects.filter(receipt_no__isnull=False).order_by('-receipt_no')[0]
        if latest:
            return (latest.receipt_no + 1)
        else:
            return 30501
        
    def next_off_voucher_no(self):
        latest = Transaction.objects.filter(off_voucher_no__isnull=False).order_by('-off_voucher_no')[0]
        if latest:
            return (latest.off_voucher_no + 1)
        else:
            return 21001
        
class Running_Balance(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)
    value = models.DecimalField(max_digits=11, decimal_places=2)

class Type_Code(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    for_office = models.BooleanField()
    
