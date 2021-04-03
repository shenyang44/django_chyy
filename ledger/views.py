from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from .models import Question, Choice, Account, Transaction, Client_Account
from django.urls import reverse
from django.views import generic
from django.utils import timezone
import json
from django.db.models import Q
import inflect


def index(request):
    accounts =  Account.objects.filter(created_at__lte=timezone.now()).exclude(file_no__startswith='EXTERNAL').exclude(file_no__startswith='OFFICE')
    balance = [acc.balance for acc in accounts]
    zipped = zip(accounts, balance)
    return render(request, 'ledger/index.html', {'zipped':zipped})

def show_off(request):
    account = get_object_or_404(Account, file_no = 'OFFICE')

    incoming_trans = account.trans_in.all()
    in_totals = [trans.total for trans in incoming_trans]
    ins = zip(incoming_trans, in_totals)

    outgoing_trans = account.trans_out.all()
    totals = [trans.total for trans in outgoing_trans]
    outs = zip(outgoing_trans, totals)

    context = {
        'account':account,
        'ins' : ins,
        'outs' : outs,
    }
    return render(request, 'ledger/office.html', context=context)

def create_acc(request):
    if request.method == 'GET':
        return render(request, 'ledger/create-acc.html')
    else:
        name = request.POST['name']
        balance = float(request.POST['balance'])
        file_no = request.POST['file_no']
        owing = request.POST['owing']
        if not owing:
            balance = float(balance)
        # else:
            # new_trans = Transaction(settled=False, receiver='carried over balance', payee='office', descriptions='Owing us from previous ') WIP
        new_acc = Account(name = name, file_no= file_no, balance = balance)
        try:
            new_acc.save()
        except:
            return render(request, 'ledger/create-acc.html', {
                'error_message' : "Error encountered in saving the account failed.",
            })
            
        return redirect(reverse('ledger:index', args=()))


def show_acc(request, acc_id):
    account = get_object_or_404(Account, pk=acc_id)
    if account.file_no.startswith('EXTERNAL'):
        return redirect(reverse('ledger:index'))
    try:
        transactions = Transaction.objects.filter(
            Q(payee=account) | Q(receiver=account)
        )
    except:
        transactions = ''
    if not transactions:
        trans_total_list = ''
    else:
        totals = [trans.total for trans in transactions]
        trans_total_list = zip(transactions, totals)

    context={
        'account':account,
        'trans_total_list': trans_total_list,
        'balance' : account.balance,
    }
    return render(request, 'ledger/show-acc.html', context=context)


def create_trans(request, acc_id):
    if request.method == 'POST':
        # retrieving form data
        table_data = json.loads(request.POST['table_data'])
        trans_type = request.POST['trans_type']
        other_party = request.POST['other_party']
        cheque_text = request.POST['cheque_text']
        other_name = request.POST['other_name']
        curr_account = get_object_or_404(Account, pk=acc_id)
        settled = True

        if other_party == 'office':
            other_party = get_object_or_404(Account, name=other_name)
        elif other_party == 'client':
            other_party = get_object_or_404(Account, file_no=other_name )
        else:
            try:
                other_party = Account.objects.get(name=other_name)
            except:
                count = 0
                count += len(Account.objects.filter(file_no__startswith='EXTERNAL'))
                other_party = Account(name=other_name, file_no=f"EXTERNAL{count}", balance=0)
                other_party.save()
    
        if trans_type == 'received':
            payee = other_party
            receiver = curr_account
            received = True
        else:
            payee = curr_account
            receiver = other_party
            received = False

        amounts=[]
        descriptions=[]
        total = 0

        # iterates over all amounts in trans, adding floated vals to total and raw text to to amounts.
        for x in table_data['amounts']:
            total += float(x)
            amounts.append(x)

        for desc in table_data['descriptions']:
            descriptions.append(desc)

        new_trans = Transaction(payee=payee, receiver=receiver, received=received, amounts=json.dumps(amounts), descriptions=json.dumps(descriptions), total=total, cheque_text=cheque_text)

        payee.balance -= total
        if payee.is_client():
            payee.client_account.balance -= total
            payee.client_account.save()

        receiver.balance += total
        if receiver.is_client():
            receiver.client_account.balance += total
            receiver.client_account.save()

        try:
            new_trans.save()
            payee.save()
            receiver.save()
        except:
            return render(request, 'ledger/transaction.html', {'account':payee, 'error_message':f'Saving the new transaction failed for: {curr_account.name}'})

        return redirect(reverse('ledger:voucher', args=(new_trans.id,)))
        
    else:
        account = get_object_or_404(Account, pk=acc_id)
        off_accs = Account.objects.filter(file_no__startswith='OFFICE')
        if account.file_no.startswith('EXTERNAL') or account.file_no.startswith('OFFICE'):
            return redirect(reverse('ledger:index'))
        return render(request, 'ledger/transaction.html', {'account':account, 'off_accs':off_accs})

def receipt_voucher_retriever(trans_id):
    transaction = get_object_or_404(Transaction, pk = trans_id)
    descriptions = json.loads(transaction.descriptions)
    amounts = json.loads(transaction.amounts)
    total = transaction.total
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
    return render(request, 'ledger/voucher.html', context=context)

def receipt(request, trans_id):
    p = inflect.engine()
    context = receipt_voucher_retriever(trans_id)
    total_worded = p.number_to_words(context['total'])
    context.update({'total_worded': total_worded})

    return render(request, 'ledger/receipt.html', context=context)

def create_cli_acc(request):
    if request.method == 'POST':
        acc_name = request.POST['acc_name']
        balance = request.POST['balance']
        new_cli_acc = Client_Account(account_no=acc_name, balance=balance)
        new_cli_acc.save()
        return redirect(reverse('ledger:index'))
    else:
        return render(request, 'ledger/create-cli-acc.html')

def create_off_acc(request):
    if request.method =='POST':

        return redirect(reverse('ledger:index'))
    else:
        return render(request, 'ledger/create-off-acc.html')

def admin_options(request):
    return render(request, 'ledger/admin-options.html')
# class ResultsView(generic.DetailView):
#     model= Question
#     template_name = 'ledger/results.html'


# class IndexView(generic.ListView):
#     template_name = 'ledger/index.html'
#     context_object_name = 'latest_list'

#     def get_queryset(self):
#         return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]

# class DetailView(generic.DetailView):
#     model = Question
#     template_name='ledger/detail.html'
#     def get_queryset(self):
#         return Question.objects.filter(pub_date__lte=timezone.now())

# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#         return render(request, 'ledger/detail.html', {
#             'question' : question,
#             'error_message' : "You didn't select a choice.",
#         })

#     selected_choice.votes += 1
#     selected_choice.save()
#     return HttpResponseRedirect(reverse('ledger:results', args=(question_id,)))
