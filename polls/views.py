from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from .models import Question, Choice, Account, Transaction
from django.urls import reverse
from django.views import generic
from django.utils import timezone
import json
from django.db.models import Q
import inflect


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_list'
    def get_queryset(self):
        return Account.objects.filter(created_at__lte=timezone.now()).exclude(file_no__startswith='EXTERNAL')

class DetailView(generic.ListView):
    model = Account
    template_name='polls/detail.html'
    def get_queryset(self):
        return Transaction.objects.filter(account_id = self.kwargs['pk'])

def create_acc(request):
    if request.method == 'GET':
        return render(request, 'polls/create-acc.html')
    else:
        name = request.POST['name']
        balance = float(request.POST['balance'])
        file_no = request.POST['file_no']
        owing = request.POST['owing']
        if owing == 1 :
            balance = int(balance * 100)
        else:
            balance = int(-(balance * 100))
        new_acc = Account(name = name, file_no= file_no, balance = balance)
        try:
            new_acc.save()
        except:
            return render(request, 'polls/create-acc.html', {
                'error_message' : "Error encountered in saving the account failed.",
            })
            
        return redirect(reverse('polls:index', args=()))


def show_acc(request, acc_id):
    account = get_object_or_404(Account, pk=acc_id)
    if account.file_no.startswith('EXTERNAL'):
        return redirect(reverse('polls:index'))
    try:
        transactions = Transaction.objects.filter(
            Q(payee=account) | Q(receiver=account)
        )
    except:
        transactions = ''
    if not transactions:
        trans_total_list = ''
    else:
        totals = [trans.total/100 for trans in transactions]
        trans_total_list = zip(transactions, totals)

    context={
        'account':account,
        'trans_total_list': trans_total_list,
    }
    return render(request, 'polls/show-acc.html', context=context)


def create_trans(request, acc_id):
    if request.method == 'POST':
        table_data = json.loads(request.POST['table_data'])
        trans_type = request.POST['trans_type']
        other_party = request.POST['other_party']
        
        cheque_text = request.POST['cheque_text']
        if other_party == 'office':
            other_party = get_object_or_404(Account, file_no='OFFICE')
        else:
            other_name = request.POST['other_name']
            try:
                other_party = Account.objects.get(name=other_name)
            except:
                count = 0
                count += len(Account.objects.filter(file_no__startswith='EXTERNAL'))
                other_party = Account(name=other_name, file_no=f"EXTERNAL{count}", balance=0)
                other_party.save()
    
        if trans_type == 'received':
            payee = other_party
            receiver = get_object_or_404(Account, pk=acc_id)
            received = True
        else:
            payee = get_object_or_404(Account, pk=acc_id) 
            receiver = other_party
            received = False

        amounts=[]
        descriptions=[]
        total = 0

        # iterates over all amounts in trans, adding inted vals to account.balance and to total, float amt to amounts.
        for x in table_data['amounts']:
            f_amount = float(x)
            amount = int(f_amount*100) 
            total += amount
            amounts.append(x)

        for desc in table_data['descriptions']:
            descriptions.append(desc)

        new_trans = Transaction(payee=payee, receiver=receiver, received=received, amounts=json.dumps(amounts), descriptions=json.dumps(descriptions), total=total, cheque_text=cheque_text)
        payee.balance -= total
        receiver.balance += total
        try:
            print(payee.id)
            new_trans.save()
            payee.save()
            receiver.save()
        except:
            return render(request, 'polls/transaction.html', {'account':payee, 'error_message':'Saving the new transaction failed for:'})

        trans_id = new_trans.id
        return redirect(reverse('polls:voucher', args=(trans_id,)))
        
    else:
        account = get_object_or_404(Account, pk=acc_id)
        return render(request, 'polls/transaction.html', {'account':account})

def receipt_voucher_retriever(trans_id):
    transaction = get_object_or_404(Transaction, pk = trans_id)
    descriptions = json.loads(transaction.descriptions)
    amounts = json.loads(transaction.amounts)
    total = transaction.total/100
    entries=[]
    for i in range(len(descriptions)):
        entries.append((descriptions[i],amounts[i]))

    con_dict = {
        'transaction':transaction,
        'entries':entries,
        'total':total,
    }
    return con_dict

def voucher(request, trans_id):
    context = receipt_voucher_retriever(trans_id)
    return render(request, 'polls/voucher.html', context=context)

def receipt(request, trans_id):
    p = inflect.engine()
    context = receipt_voucher_retriever(trans_id)
    total_worded = p.number_to_words(context['total'])
    context.update({'total_worded': total_worded})

    return render(request, 'polls/receipt.html', context=context)

# class IndexView(generic.ListView):
#     template_name = 'polls/index.html'
#     context_object_name = 'latest_list'

#     def get_queryset(self):
#         return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

# class DetailView(generic.DetailView):
#     model = Question
#     template_name='polls/detail.html'
#     def get_queryset(self):
#         return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model= Question
    template_name = 'polls/results.html'

# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#         return render(request, 'polls/detail.html', {
#             'question' : question,
#             'error_message' : "You didn't select a choice.",
#         })

#     selected_choice.votes += 1
#     selected_choice.save()
#     return HttpResponseRedirect(reverse('polls:results', args=(question_id,)))
