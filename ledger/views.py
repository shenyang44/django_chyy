from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from .models import Account, Transaction, Client_Account, Running_Balance
from django.urls import reverse
from django.views import generic
from django.utils import timezone
import json
from django.db.models import Q
import inflect
from decimal import Decimal


def index(request):
    accounts =  Account.objects.filter(created_at__lte=timezone.now()).exclude(file_no__startswith='EXTERNAL').exclude(file_no__startswith='OFFICE')
    balance = [acc.balance for acc in accounts]
    zipped = zip(accounts, balance)
    return render(request, 'ledger/index.html', {'zipped':zipped})

def show_off(request):
    off_accs = Account.objects.filter(file_no__startswith = 'OFFICE')
    transactions_list = []
    for off_acc in off_accs:
        transactions = Transaction.objects.filter(Q(payee = off_acc) | Q(receiver = off_acc)).order_by('-created_at')
        entries_list =[]
        rb_list = []
        for trans in transactions:
            descriptions = json.loads(trans.descriptions)
            amounts = json.loads(trans.amounts)
            entries_list.append(zip(descriptions, amounts))
            try:
                rb = Running_Balance.objects.get(account = account, transaction=trans)
                rb_list.append(rb.value)
            except:
                rb_list.append('fail')
        transactions_list.append(zip(transactions, entries_list, rb_list))
    
    office_data = zip(off_accs, transactions_list)

    context = {
        'off_accs':off_accs,
        'office_data':office_data,
    }
    return render(request, 'ledger/office.html', context=context)

def show_cli(request):
    client_accs = Client_Account.objects.all()
    accounts = [cli_acc.account_set.all() for cli_acc in client_accs]
    totals = [cli_acc.balance() for cli_acc in client_accs]
    for each in client_accs:
        print(each.balance())
    acc_data = zip(client_accs, accounts, totals)
    context = {
        'acc_data':acc_data,
        'client_accs': client_accs,
    }
    return render(request, 'ledger/client.html', context=context)

def create_acc(request):
    if request.method == 'GET':
        return render(request, 'ledger/create-acc.html', {'cli_accs':Client_Account.objects.all()})
    else:
        name = request.POST['name']
        balance = Decimal(request.POST['balance'])
        file_no = request.POST['file_no']
        owing = request.POST['owing']
        client_acc_id = request.POST['client']

        if not owing:
            balance = Decimal(balance)
        # else:
            # new_trans = Transaction(settled=False, receiver='carried over balance', payee='office', descriptions='Owing us from previous ') WIP
        new_acc = Account(name = name, file_no= file_no, balance = balance, client_account=client_acc_id)
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

    entries_list=[]
    rb_list=[]
    for trans in transactions:
        descriptions = json.loads(trans.descriptions)
        amounts = json.loads(trans.amounts)
        entries = []
        for i in range(len(descriptions)):
            entries.append((descriptions[i],amounts[i]))
        entries_list.append(entries)
        try:
            rb = Running_Balance.objects.get(account = account, transaction=trans)
            rb_list.append(rb.value)
        except:
            rb_list.append('fail')
        

    context={
        'account':account,
        'trans_zipped': zip(transactions, entries_list, rb_list)
    }
    return render(request, 'ledger/show-acc.html', context=context)

def off_trans(request, acc_id):
    if request.method == 'GET':
        return render(request, 'ledger/off-trans.html')
    else:

        if curr_account == payee:
            return redirect(reverse('ledger:voucher', args=(new_trans.id,)))
        else:
            return redirect(reverse('ledger:receipt', args=(new_trans.id,)))
def create_trans(request, acc_id):
    if request.method == 'POST':
        # retrieving form data
        table_data = json.loads(request.POST['table_data'])
        trans_type = request.POST['trans_type']
        other_party = request.POST['other_party']
        cheque_text = request.POST['cheque_text']
        other_name = request.POST['other_name']
        curr_account = get_object_or_404(Account, pk=acc_id)

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
        else:
            payee = curr_account
            receiver = other_party

        amounts=[]
        descriptions=[]
        total = 0

        # iterates over all amounts in trans, adding floated vals to total and raw text to to amounts.
        for x in table_data['amounts']:
            total += Decimal(x)
            amounts.append(x)

        for desc in table_data['descriptions']:
            descriptions.append(desc)

        new_trans = Transaction(payee=payee, receiver=receiver, amounts=json.dumps(amounts), descriptions=json.dumps(descriptions), total=total, cheque_text=cheque_text)
        payee.balance -= total
        receiver.balance += total

        try:
            new_trans.save()
            payee.save()
            receiver.save()
        except:
            return render(request, 'ledger/transaction.html', {'account':payee, 'error_message':f'Saving the new transaction failed for: {curr_account.name}'})

        payee_rb = Running_Balance(account = payee, transaction = new_trans, value = payee.balance)
        receiver_rb = Running_Balance(account=receiver, transaction=new_trans, value=receiver.balance)
        try:
            payee_rb.save()
            receiver_rb.save()
        except:
            return render(request, 'ledger/transaction.html', {'account':payee, 'error_message':f'Saving the new transaction failed for: {curr_account.name}'})
        if curr_account == payee:
            return redirect(reverse('ledger:voucher', args=(new_trans.id,)))
        else:
            return redirect(reverse('ledger:receipt', args=(new_trans.id,)))
        
    else:
        account = get_object_or_404(Account, pk=acc_id)
        other_cli_accs = Account.objects.filter(client_account__isnull=False).exclude(id = account.id)
            
        file_no_list = [acc.file_no for acc in other_cli_accs]

        off_accs = Account.objects.filter(file_no__startswith='OFFICE')
        if account.is_external():
            return redirect(reverse('ledger:index'))
        
        context = {
            'account':account,
            'off_accs':off_accs,
            'file_no_list': json.dumps(file_no_list) 
        }
        return render(request, 'ledger/transaction.html', context=context)

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
        # balance = request.POST['balance']
        new_cli_acc = Client_Account(name=acc_name)
        new_cli_acc.save()
        return redirect(reverse('ledger:index'))
    else:
        return render(request, 'ledger/create-cli-acc.html')

def create_off_acc(request):
    if request.method =='POST':
        name = request.POST['acc_name']
        balance = Decimal(request.POST['balance'])
        file_no = 'OFFICE' + name
    
        new_acc = Account(name = name, file_no= file_no, balance = balance)
        try:
            new_acc.save()
        except:
            return render(request, 'ledger/create-off-acc.html', {
                'error_message' : "Error encountered in saving the account failed.",
            })
        return redirect(reverse('ledger:index'))
    else:
        return render(request, 'ledger/create-off-acc.html')

def admin_options(request):
    return render(request, 'ledger/admin-options.html')

def search(request):
    if request.method == "POST":
        search_q = request.POST['search_q']
        # an OR query to see if either NAME or FILE_NO field contain the searched string (case insensitive)
        accounts = Account.objects.filter(Q(file_no__icontains = search_q) | Q(name__icontains = search_q)).exclude(file_no__startswith = 'EXTERNAL')
        return render(request, 'ledger/search.html', {'accs':accounts, 'search_q':search_q,})