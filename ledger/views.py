from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Account, Transaction, Client_Account, Running_Balance, Type_Code
from django.urls import reverse
from django.utils import timezone
import json
from django.db.models import Q
import inflect
from decimal import Decimal
from django.contrib import messages
from datetime import date, datetime, time, timedelta
import math, copy

def brace_num(x):
    if x < 0:
        return f'({str(abs(x))})'
    else:
        return x

def index(request):
    accounts =  Account.objects.filter(created_at__lte=timezone.now()).filter(client_account=True).order_by('-updated_at')
    if len(accounts) > 0:
        balance = [brace_num(acc.balance) for acc in accounts]
        zipped = zip(accounts, balance)
    else:
        zipped = None
    return render(request, 'ledger/index.html', {'zipped':zipped})

def show_off(request, off_id=None):
    date_from = datetime.strptime('2020/01/01', "%Y/%m/%d")
    date_to=timezone.localdate()
    if request.method == 'POST':
        if not off_id:
            off_id = request.POST.get('off_id')
        date_from_inp = request.POST.get('date_from')
        date_to_inp = request.POST.get('date_to')        
        checked = request.POST.get('checked')
        trans_id = request.POST.get('trans_id')
        new_name = request.POST.get('new_name')
        if new_name:
            try:
                off_acc = Account.objects.get(pk=off_id)
                old_name = off_acc.name
                off_acc.name = new_name
                off_acc.save()
                messages.success(request, f'Office account name was changed successfully from {old_name} to {off_acc.name}')
            except:
                messages.error(request, 'Name change failed.')
        elif checked:
            try:
                off_acc = Account.objects.get(pk=off_id)
                trans = Transaction.objects.get(pk=trans_id)
                if checked  == 'true':
                    trans.checked = True
                else:
                    trans.checked = False
                trans.save()
            except:
                messages.warning(request, 'Could not locate office account in database.')
        else:
            date_from = datetime.strptime(date_from_inp, "%Y/%m/%d")
            date_to = datetime.strptime(date_to_inp, "%Y/%m/%d")

    date_to += timedelta(days=1)

    off_accs = Account.objects.filter(file_no__startswith = 'OFFICE').order_by('created_at')
    transactions_list = []
    for off_acc in off_accs:
        transactions = Transaction.objects.filter(Q(payee = off_acc) | Q(receiver = off_acc)).filter(cleared=True).filter(created_at__lte=date_to).filter(created_at__gte=date_from).order_by('created_at')
        entries_list =[]
        rb_list = []
        for trans in transactions:
            entries_list.append(json.loads(trans.table_list))
            try:
                rb = Running_Balance.objects.get(account = off_acc, transaction=trans)
                rb_list.append(rb.value)
            except:
                rb_list.append('fail')
        transactions_list.append(zip(transactions, entries_list, rb_list))
    
    office_data = zip(off_accs, transactions_list)
    
    try:
        off_id = int(off_id)
    except:
        off_id = None
    date_to -= timedelta(days=1)
    
    context = {
        'selected': off_id,
        'off_accs':off_accs,
        'office_data':office_data,
        'date_to':date_to.strftime('%Y/%m/%d'),
        'date_from':date_from.strftime('%Y/%m/%d'),
    }
    return render(request, 'ledger/office.html', context=context)

def show_cli(request):
    if request.method == 'POST':
        date_input = request.POST['date_to']
        date_to = datetime.strptime(date_input, "%d/%m/%Y")
    else:
        date_to=timezone.localdate()
    
    accounts = Account.objects.filter(client_account=True, created_at__lte=date_to+timedelta(days=1))
    rbs = []
    total = Decimal(0.00)
    for acc in accounts:
        try:
            last_rb = Running_Balance.objects.filter(account_id=acc.id, created_at__lte=date_to+timedelta(days=1)).order_by('-created_at')[0].value
        except:
            last_rb = Decimal(0.00)
            messages.error(request, f'File with client code: {acc.client_code} does not have any running balance prior to date selected')
        total += last_rb
        
        rbs.append(brace_num(last_rb))
    
    entries_list=[]
    dupe = []
    transactions = Transaction.objects.filter(Q(payee__client_account = True) | Q(receiver__client_account = True)).order_by('created_at')
    for trans in transactions:
        entries_list.append(json.loads(trans.table_list))
        if trans.payee.client_account == True and trans.receiver.client_account==True:
            dupe.append(True)
        else:
            dupe.append(False)

    trans_zip = zip(transactions, entries_list, dupe)
    total = brace_num(total)
    context = {
        'accounts_data': zip(accounts,rbs),
        'total': total,
        'date_to' : date_to,
        'file_count' : len(accounts),
        'trans_zip':trans_zip,
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
        subject_matter = request.POST['subject_matter']
        client_code = request.POST['client_code']
        subj_list = json.dumps([subject_matter])
        if owing == 'no':
            balance = -(Decimal(balance))
        else:
            balance = Decimal(balance)
        new_acc = Account(name = name, file_no= file_no, balance = balance, client_account=True, client_code=client_code, subj_list=subj_list, subject_matter=subject_matter)
        try:
            ext_acc = Account.objects.get(file_no='EXTERNAL_balance_b/f')
        except:
            ext_acc = Account(name='Balance b/f', file_no='EXTERNAL_balance_b/f', balance=0.00)
            ext_acc.save()
        if owing == 'no':
            receiver = new_acc
            payee = ext_acc
        else:
            receiver = ext_acc
            payee = new_acc
        first_trans = Transaction(receiver=receiver, payee=payee, table_list=json.dumps([{'description':'Balance brought forward.', 'amount':'','type_code':''}]), total=abs(balance), category='NA')
        try:
            new_acc.save()
            first_trans.save()
        except:
            messages.error(request, 'Error encountered in saving the account.')
            return render(request, 'ledger/create-acc.html')
        
        new_rb = Running_Balance(account=new_acc, value=balance, transaction=first_trans)
        try:
            new_rb.save()
        except:
            messages.error(request, 'Error encountered in recording initial balance.')
            return redirect(reverse('ledger:show_acc', args=(new_acc.id,)))

        return redirect(reverse('ledger:show_acc', args=(new_acc.id,)))

def show_acc(request, acc_id):
    if request.method == 'POST':
        date_from_inp = request.POST['date_from']
        date_to_inp = request.POST['date_to']
        date_from = datetime.strptime(date_from_inp, "%Y/%m/%d")
        date_to = datetime.strptime(date_to_inp, "%Y/%m/%d")
    else:
        date_from = datetime.strptime('2020/01/01', "%Y/%m/%d")
        date_to=timezone.localdate()

    date_to += timedelta(days=1)
    try:
        account = Account.objects.get(pk=acc_id)
    except:
        messages.error(request, 'That account does not exist. If you believe this to be a mistake, click on help button.')
        return redirect(reverse('ledger:index'))
    if account.is_external() or account.is_office():
        messages.warning(request, 'Sorry but that account is not viewable. If you believe this is an error, please click on help button.')
        return redirect(reverse('ledger:index'))
    try:
        transactions = Transaction.objects.filter(
            Q(payee=account) | Q(receiver=account)
        ).filter(created_at__lte=date_to).filter(created_at__gte=date_from).order_by('created_at')
    except:
        transactions = ''

    entries_list=[]
    rb_list=[]
    for trans in transactions:
        entries_list.append(json.loads(trans.table_list))
        try:
            rb = Running_Balance.objects.get(account = account, transaction=trans)
            rb_list.append(brace_num(rb.value))
        except:
            rb_list.append('fail')
        
    balance = brace_num(account.balance)
    date_to -= timedelta(days=1)

    try:
        json_subj_list = account.subj_list
        subj_list = json.loads(json_subj_list)
        subj_list.remove(account.subject_matter)
    except:
        subj_list=None
        if account.subject_matter:
            account.subj_list = json.dumps([account.subject_matter])
            account.save()
            json_subj_list = account.subj_list
        else:
            json_subj_list = '[]'

    context={
        'account':account,
        'trans_zipped': zip(transactions, entries_list, rb_list),
        'balance' : balance,
        'date_from': date_from.strftime('%Y/%m/%d'),
        'date_to': date_to.strftime('%Y/%m/%d'),
        'subj_list': subj_list,
        'json_subj_list' : json_subj_list,
    }
    return render(request, 'ledger/show-acc.html', context=context)

def edit_info(request, acc_id):
    if request.method == "POST":
        new_name = request.POST.get('name')
        new_code = request.POST.get('code')
        new_ref = request.POST.get('ref')
        account = Account.objects.get(pk = acc_id)
        if new_name:
            account.name = new_name
        elif new_code:
            account.client_code = new_code
        elif new_ref:
            account.file_no = new_ref
        else:
            messages.error(request, 'No information was received in edit_info function.')
        account.save()
        return redirect(reverse('ledger:show_acc', args=(acc_id,)))

def balance_edit(request):
    if request.method == 'POST':
        acc_id = request.POST['acc_id']
        new_balance = Decimal(request.POST['new_balance'])
        owing_us = request.POST['owing_us']
        acc = Account.objects.get(pk=acc_id)
        if owing_us == 'yes':
            acc.balance = new_balance
        else:
            acc.balance = -new_balance
        try:
            acc.save()
            return(JsonResponse({'balance':brace_num(acc.balance), 'status':'success'}))
        except:
            return(JsonResponse({'status':'error'}))
        
def subj_matter(request, acc_id):
    if request.method == 'POST':
        new_subj = request.POST.get('new_subj')
        new_default = request.POST.get('new_default')
        to_edit = request.POST.get('to_edit')
        edited_name = request.POST.get('edited_name')
        account = Account.objects.get(pk=acc_id)

        try:
            subj_list = json.loads(account.subj_list)
        except:
            if account.subject_matter:
                subj_list = [account.subject_matter]
            else:
                subj_list = []

        if new_subj:
            subj_list.append(new_subj)
        elif to_edit:
            subj_list[subj_list.index(to_edit)] = edited_name
            if account.subject_matter == to_edit:
                account.subject_matter = edited_name
        elif new_default:
            account.subject_matter = new_default

        account.subj_list = json.dumps(subj_list)
        account.save()
        return redirect(reverse('ledger:show_acc', args=(acc_id,)))

# saves client file opening and closing dates, along with file closing no.
def opening_closing(request):
    if request.method == 'POST':
        opening_date = request.POST.get('opening_input')
        closing_date = request.POST.get('closing_input')
        closing_no = request.POST.get('closing_file_no')
        acc_id = request.POST['acc_id']
        curr_acc = Account.objects.get(pk = acc_id)

        if opening_date:
            opening_date = datetime.strptime(opening_date, '%Y/%m/%d')
            curr_acc.opening_date = opening_date
            error = 'opening date'
        elif closing_date and closing_no:
            closing_date = datetime.strptime(closing_date, '%Y/%m/%d')
            curr_acc.closing_date = closing_date
            curr_acc.closing_no = closing_no
            error = 'closing date'
        else:
            messages.error(request, 'Server did not receive opening/closing date/closing no.')
            return redirect(reverse('ledger:show_acc', args=(curr_acc.id,)))

        try:
            curr_acc.save()
        except:
            messages.error(request, f'Could not save client file {error}.')

        return redirect(reverse('ledger:show_acc',  args=(curr_acc.id,)))

def tax(request, acc_id):
    if request.method == 'POST':
        date_from_inp = request.POST['date_from']
        date_to_inp = request.POST['date_to']
        date_from = datetime.strptime(date_from_inp, "%Y/%m/%d")
        date_to = datetime.strptime(date_to_inp, "%Y/%m/%d")
    else:
        date_from = datetime.strptime('1900/01/01', "%Y/%m/%d")
        date_to=timezone.localdate()
    
    date_to += timedelta(days=1)
    curr_acc = Account.objects.get(pk = acc_id)
    trans = Transaction.objects.filter(payee=curr_acc,created_at__lte=date_to).filter(created_at__gte=date_from)
    total = 0
    ps_trans = []

    for each in trans:
        entries = json.loads(each.table_list)
        for entry in entries:
            if entry['type_code'] == 'PS':
                try:
                    total += Decimal(entry['amount'])
                except:
                    pass
                entry.update({"id" : each.id, "created_at": each.created_at})
                ps_trans.append(entry)
    date_to -= timedelta(days=1)
    context = {
        'account': curr_acc,
        'total': total,
        'trans': ps_trans,
        'date_from':date_from.strftime("%Y/%m/%d"),
        'date_to':date_to.strftime("%Y/%m/%d"),
    }
    return render(request, 'ledger/tax.html', context=context)

def total_tax(request):
    if request.method == 'POST':
        date_from_inp = request.POST['date_from']
        date_to_inp = request.POST['date_to']
        date_from = datetime.strptime(date_from_inp, "%Y/%m/%d")
        date_to = datetime.strptime(date_to_inp, "%Y/%m/%d")
    else:
        date_from = datetime.strptime('1900/01/01', "%Y/%m/%d")
        date_to=timezone.localdate()
    
    date_to += timedelta(days=1)
    trans = Transaction.objects.filter(receiver__file_no__startswith='OFFICE',created_at__lte=date_to).filter(created_at__gte=date_from)
    total = 0
    ps_trans = []

    for each in trans:
        entries = json.loads(each.table_list)
        for entry in entries:
            if entry['type_code'] == 'PS':
                try:
                    total += Decimal(entry['amount'])
                except:
                    pass
                entry.update({"id" : each.id, "created_at": each.created_at})
                ps_trans.append(entry)
    date_to -= timedelta(days=1)
    context = {
        'total': total,
        'trans': ps_trans,
        'date_from':date_from.strftime("%Y/%m/%d"),
        'date_to':date_to.strftime("%Y/%m/%d"),
    }
    return render(request, 'ledger/total_tax.html', context=context)

def trans_cont(acc_id):
    account = get_object_or_404(Account, pk=acc_id)
    other_cli_accs = Account.objects.filter(client_account__isnull=False).exclude(id = account.id)
        
    file_no_list = [acc.file_no for acc in other_cli_accs]

    off_accs = Account.objects.filter(file_no__startswith='OFFICE').order_by('created_at')
    if account.is_external():
        return redirect(reverse('ledger:index'))
    
    cli_accs = Client_Account.objects.all()
    if account.is_office():
        type_codes = Type_Code.objects.filter(for_office=True)
    else:
        type_codes = Type_Code.objects.filter(for_office=False)

    tc_dict = {}
    for each in type_codes:
        tc_dict[each.code] = each.description
    balance = brace_num(account.balance)

    if account.subj_list:
        subj_list = json.loads(account.subj_list)
        subj_list.remove(account.subject_matter)
    else:
        subj_list=None
    
    context = {
        'account':account,
        'off_accs':off_accs,
        'file_no_list': json.dumps(file_no_list),
        'balance' : balance,
        'cli_accs': cli_accs,
        'tc_dict': json.dumps(tc_dict),
        'subj_list': subj_list,
    }
    return context

def trans_save_err(request, acc_id):
    account = get_object_or_404(Account, pk = acc_id)
    messages.error(request, f'Saving the new transaction failed for: {account.name}')
    return render(request, 'ledger/transaction.html', {'account':account})

def create_trans(request, acc_id, trans_type):
    if request.method == 'POST':
        # retrieving form data
        table_list = json.loads(request.POST['table_data'])
        other_party = request.POST['other_party']
        cheque_text = request.POST['cheque_text']
        other_name = request.POST['other_name']
        curr_account = get_object_or_404(Account, pk=acc_id)
        subject_matter = request.POST.get('subject_matter')
        resolved = True
        # model self ref prop is none unless it is an advance disburse, in which case, it links to the transaction made on the Off Acc.
        ad_link = None
        try:
            cli_acc_name = request.POST['cli_acc_name']
            cli_acc = Client_Account.objects.get(name = cli_acc_name)
        except:
            cli_acc = None

        if other_party == 'office':
            other_party = get_object_or_404(Account, id=other_name)
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
    
        if trans_type == 'cre':
            payee = other_party
            receiver = curr_account
        else:
            payee = curr_account
            receiver = other_party

        total = 0
        adv_trans = False

        # iterates over each dict adding decimal vals to total and checking if trans is advanced transfer.
        table_list_cpy = copy.deepcopy(table_list)
        for each in table_list_cpy:
            if each['amount']:
                total += Decimal(each['amount'])
            if each['type_code'] in ['AD', 'AT']:
                adv_trans = True
                each['description'] = f"{curr_account.client_code} | {each['description']}"
        
        # handling for advance disbursements.
        if adv_trans:
            off_id = request.POST['off_id']
            off_acc = Account.objects.get(id = off_id)
            off_trans = Transaction(payee=off_acc, receiver=receiver, table_list=json.dumps(table_list_cpy), total=total, cheque_text=cheque_text, resolved=False, off_voucher_no=Transaction.next_off_voucher_no(None))
            off_acc.balance -= total
            try:
                off_acc.save()
                off_trans.save()
            except:
                return trans_save_err(request, curr_account.id)
            ad_link = off_trans
            off_rb = Running_Balance(account=off_acc, transaction=off_trans, value=off_acc.balance)
            try:
                off_rb.save()
            except:
                return trans_save_err(request, curr_account.id)

        v_no = None
        r_no = None
        off_v_no = None
        if payee.is_office():
            payee.balance -= total
            off_v_no = Transaction.next_off_voucher_no(None)
        elif payee.client_account:
            payee.balance += total
            v_no = Transaction.next_voucher_no(None)

        # if receiver is office acc, not credited yet, waiting to be cleared from the off acc page.
        cleared = True
        if receiver.client_account:
            receiver.balance -= total
            r_no = Transaction.next_receipt_no(None)
        else:
            cleared = False

        new_trans = Transaction(payee=payee, receiver=receiver, table_list=json.dumps(table_list), total=total, cheque_text=cheque_text, resolved=resolved, ad_link=ad_link, cli_acc=cli_acc, cleared=cleared, subj_matter=subject_matter, receipt_no = r_no, voucher_no=v_no, off_voucher_no=off_v_no)
            
        try:
            new_trans.save()
            payee.save()
            receiver.save()
        except:
            return trans_save_err(request, curr_account.id)

        try:
            payee_rb = Running_Balance(account = payee, transaction = new_trans, value = payee.balance)
            payee_rb.save()
            if cleared:
                receiver_rb = Running_Balance(account=receiver, transaction=new_trans, value=receiver.balance)
                receiver_rb.save()
        except:
            return trans_save_err(request, curr_account.id)

        if curr_account == payee:
            return redirect(reverse('ledger:voucher', args=(new_trans.id,)))
        else:
            if curr_account.is_office():
                return redirect(reverse('ledger:show_off', args=(curr_account.id,)))
            return redirect(reverse('ledger:receipt', args=(new_trans.id,)))
        
    else:
        context = trans_cont(acc_id)
        context.update({
            'trans_type':trans_type,
            'adat':False,
        })
        return render(request, 'ledger/transaction.html', context=context)

def counter_trans(request):
    if request.method == 'POST':
        trans_id = request.POST['trans_id']
        acc_id = int(request.POST['acc_id'])
        try:
            trans = Transaction.objects.get(pk=trans_id)
            acc = Account.objects.get(pk=acc_id)
        except:
            messages.error(request, 'Could not retrieve the transaction or account.')
            return redirect(reverse('ledger:index'))
        payee = trans.payee
        receiver = trans.receiver
        total = trans.total
        cleared = trans.cleared
        entry = [{
            'description':trans_id,
            'amount':str(total),
            'type_code':'NA'
        }]

        try:
            cancel_acc = Account.objects.get(file_no='EXTERNAL_cancel_acc')
        except:
            cancel_acc= Account(name='Transaction Cancellation acc', file_no='EXTERNAL_cancel_acc', balance=0)
            cancel_acc.save()

        if not cleared:
            receiver = cancel_acc
            payee.balance -= total
            new_trans = Transaction(total=total, receiver=payee, payee=receiver, table_list=json.dumps(entry), category='NA', cli_acc=trans.cli_acc, cleared=True, cheque_text='cancellation')
            trans.receiver = receiver
        else:
            if payee.is_office():
                payee.balance += total
            else:
                payee.balance -= total
            if receiver.is_office():
                receiver.balance -= total
            else:
                receiver.balance += total
            new_trans = Transaction(total=total, receiver=payee, payee=receiver, table_list=json.dumps(entry), category='NA', cli_acc=trans.cli_acc, cleared=True, cheque_text='cancellation')
        
        try:
            trans.save()
            new_trans.save()
            payee.save()
            receiver.save()
            rb_p = Running_Balance(account=payee, transaction=new_trans, value=payee.balance)
            rb_r = Running_Balance(account=receiver, transaction=new_trans, value=receiver.balance)
            rb_p.save()
            rb_r.save()
        except:
            messages.error(request, 'Error occurred while saving counter transaction.')

        if acc.is_office():
            return redirect(reverse('ledger:show_off', args=(acc_id,)))
        else:
            return redirect(reverse('ledger:show_acc', args=(acc_id,)))

def create_ad(request, acc_id):
    curr_acc = get_object_or_404(Account, pk = acc_id)
    if curr_acc.is_office() or curr_acc.is_external():
        messages.warning(request, 'Only client files can make AD/AT transactions.')
        return redirect(reverse('ledger:index'))
    context = trans_cont(acc_id)
    context.update({
        'trans_type':'deb',
        'adat': True,
    })
    return render(request, 'ledger/transaction.html', context=context )

def receipt_voucher_retriever(trans_id):
    transaction = get_object_or_404(Transaction, pk = trans_id)
    table_list = json.loads(transaction.table_list)

    con_dict = {
        'transaction':transaction,
        'entries':table_list,
        'total': transaction.total,
    }
    return con_dict

def voucher(request, trans_id):
    context = receipt_voucher_retriever(trans_id)
    context.update({
        'account':context['transaction'].payee
    })
    return render(request, 'ledger/voucher.html', context=context)

def receipt(request, trans_id):
    trans = get_object_or_404(Transaction, pk = trans_id)
    if trans.receiver.is_external() or trans.receiver.is_office():
        messages.warning(request, 'Only client files can view receipts, not available for office or external accounts.')
        return redirect(reverse('ledger:index'))
    p = inflect.engine()
    context = receipt_voucher_retriever(trans_id)
    total = context['total']
    before_pt = math.floor(total)
    before_pt_worded = p.number_to_words(before_pt)
    after_pt = int((total - before_pt) * 100)
    after_pt_worded = p.number_to_words(after_pt)
    total_worded = before_pt_worded + ' and ' + after_pt_worded + ' cents'
    
    context.update({
        'account':context['transaction'].receiver,
        'total_worded': total_worded.title()
    })

    return render(request, 'ledger/receipt.html', context=context)

def create_cli_acc(request):
    if request.method == 'POST':
        acc_name = request.POST['acc_name']
        acc_number = request.POST['acc_number']
        bank_name = request.POST['bank_name']
        bank_code = request.POST['bank_code']
        new_cli_acc = Client_Account(name=acc_name, bank_code=bank_code, acc_number=acc_number, bank_name=bank_name)
        new_cli_acc.save()
        return redirect(reverse('ledger:index'))
    else:
        return render(request, 'ledger/create-cli-acc.html')

def create_off_acc(request):
    if request.method =='POST':
        name = request.POST['acc_name']
        client_code = request.POST['bank']
        balance = Decimal(request.POST['balance'])
        count = 0
        count += len(Account.objects.filter(file_no__startswith='OFFICE'))
        file_no = f'OFFICE{count}'
        new_acc = Account(name = name, file_no=file_no, balance = balance, client_code=client_code)
        try:
            new_acc.save()
        except:
            messages.error(request, 'Error encountered in saving the account.')
            return render(request, 'ledger/create-off-acc.html')
        return redirect(reverse('ledger:index'))
    else:
        return render(request, 'ledger/create-off-acc.html')

def create_tc(request):
    if request.method == "GET":
        type_codes = Type_Code.objects.all()
        tc_list = ['RD', 'RD1', 'RD2', 'RD3', 'RD4', 'RD5', 'RD6', 'RD7', 'RD8', 'RD11', 'RD14', 'RD15', 'RD17', 'RF', 'RI', 'RO', 'RFDG', 'RS', 'RT', 'RT1', 'RT2', 'RT3', 'RT4', 'RT5', 'RT6', 'RT7', 'RT8', 'RT9', 'RT10', 'RT11', 'RT12', 'RT13','PD', 'PD1', 'PD2', 'PD3', 'PD4', 'PD5', 'PD6', 'PD7', 'PD8', 'PD9', 'PD10', 'PD11', 'PD12', 'PD13', 'PD14', 'PD15', 'PD16', 'PD17', 'PD18', 'PF', 'PI', 'PO', 'PS', 'PT', 'PT1', 'PT2', 'PT3', 'PT4', 'PT5', 'PT6', 'PT7', 'PT8', 'PT9', 'PT10', 'PT11', 'PT12', 'PT13', '0501','1019','6001','6002','ADBOOK','ADCOMP','ADF&F','ADHAND','ADOE','ADRENO','ADV1','ADV2','ADV3','ADV4','ADV5','ADV6','ADV7','ADV8','ADV9','CA1','CA10','CA11','CA12','CA13','CA14','CA15','CA16','CA2','CA3','CA4','CA5','CA6','CA7','CA8','CA9','CAP1','CAP2','CL1','CL10','CL11','CA17','CL12','CL13','CL14','CL17','CL18','CL19','CL2','CL20','CL21','CL22','CL3','CL4','CL5','CL6','CL7','CL8','CL9','CURRT1','CURRT2','DRAW1','DRAW2','DRAW3','EXP','EXP1','EXP10','EXP11','EXP12','EXP13','EXP14','EXP15','EXP16','EXP17','EXP18','EXP19','EXP2','EXP20','EXP21','EXP22','EXP23','EXP24','EXP25','EXP26','EXP27','EXP28','EXP29','EXP3','EXP30','EXP31','EXP33','EXP34','EXP35','EXP36','EXP37','EXP38','EXP39','EXP4','EXP40','EXP41','EXP42','EXP43','EXP44','EXP45','EXP46','EXP47','EXP48','EXP49','EXP5','EXP50','EXP51','EXP52','EXP53','EXP54','EXP55','EXP56','EXP57','EXP58','EXP59','EXP6','EXP60','EXP61','EXP62','EXP63','EXP64','EXP65','EXP66','EXP67','EXP68','EXP69','EXP7','EXP70','EXP71','EXP72','EXP73','EXP74','EXP75','EXP76','EXP77','EXP78','EXP79','EXP8','EXP80','EXP81','EXP82','EXP83','EXP84','EXP85','EXP86','EXP9','FABOOK','FACOMP','FAF&F','FAH/P','FAOE','FARENO','FAV1','FAV2','FAV3','FAV4','FAV5','FAV6','FAV7','FAV8','FAV9','INC1','INC2','INC3','INC4','EXP87','EXP88','EXP89','EXP90','INC6']
        
        for each in type_codes:
            tc_list.append(each.code)

        context = {
            'type_codes': type_codes,
            'tc_list': json.dumps(tc_list),
        }
        return render(request, 'ledger/create-tc.html', context=context)
    else:
        code = request.POST['code']
        description = request.POST['description']
        for_office = request.POST.get('for_office')
        if for_office == 'yes':
            for_office = True
        else:
            for_office = False
            
        new_tc = Type_Code(code = code, description = description, for_office=for_office)
        try: 
            new_tc.save()
        except:
            messages.error(request,'Could not save new type code addition.')
        return redirect(reverse('ledger:create_tc'))

def remove_tc(request, tc_id):
    if request.method == 'GET':
        try:
            Type_Code.objects.get(pk = tc_id).delete()
            messages.success(request, 'Type code was successfully deleted.')       
        except:
            messages.error(request, 'There was an issue in attempting to delete type code.')
        
        return redirect(reverse('ledger:create_tc'))

def adat_index(request):
    if request.method == "GET":
        unresolved_trans = Transaction.objects.filter(resolved = False, ad_link__isnull = True)
        total = 0
        entries_list=[]
        for trans in unresolved_trans:
            total += trans.total
            entries_list.append(json.loads(trans.table_list))
            
        context = {
            'total': total,
            'trans_zipped': zip(unresolved_trans, entries_list),
        }
        return render(request, 'ledger/adat-index.html', context=context)

def resolve(request, trans_id):
    if request.method == "GET":
        try:
            trans = Transaction.objects.get(pk=trans_id)
        except:
            messages.error(request,'Transaction that was attempted to be cleared could not be retrieved.')
            return redirect(reverse('ledger:adat_index'))
        cli_trans = trans.cli_ad_link.get()
        curr_acc = cli_trans.payee
        off_acc = trans.payee
        balance = brace_num(curr_acc.balance)
        context= receipt_voucher_retriever(cli_trans.id)
            
        context.update({
            'acc':curr_acc,
            'off_acc':off_acc,
            'balance': balance,
            'off_trans':trans
        })
        return render(request, 'ledger/resolve.html', context=context)

    else:
        try:
            trans = Transaction.objects.get(pk=request.POST['trans_id'])
            off_trans = Transaction.objects.get(pk=request.POST['off_trans_id'])
            acc = Account.objects.get(pk=request.POST['acc_id'])
            off_acc = Account.objects.get(pk=request.POST['off_acc_id'])
        except:
            messages.error(request, 'Advance disbursement resolution failed, could not retrieved transaction/account object(s).')
            return redirect(reverse('ledger:adat_index'))
        
        total = trans.total
        table_list=[{
            'description':f'Payment reimbursement from clients account for office PV{off_trans.off_voucher_no}',
            'amount': f'{trans.total}',
            'type_code':'AT'
        }]
        
        new_trans = Transaction(payee=acc, receiver=off_acc, table_list=json.dumps(table_list), total=total, cheque_text='customisable', voucher_no=Transaction.next_voucher_no(None))
        table_list=[{
            "description": f"Payment reimbursement from clients account for PV{trans.voucher_no}",
            "amount":f"{trans.total}",
            "type_code":"AT"
        }]
        try:
            auth_acc = Account.objects.get(file_no='EXTERNAL_auth_acc')
        except:
            auth_acc= Account(name='Account for Pre-auth Debit', file_no='EXTERNAL_auth_acc', balance=0)
            auth_acc.save()
        pre_auth_debit = Transaction(payee=auth_acc, receiver=acc, table_list=json.dumps(table_list), total=total, cheque_text='customisable', receipt_no= Transaction.next_receipt_no(None), receipt_ref=f'Office account voucher no.{off_trans.off_voucher_no}')
        trans.resolved = True
        off_trans.resolved = True
        off_acc.balance += total
        try:
            pre_auth_debit.save()
            trans.save()
            off_trans.save()
            off_acc.save()
            new_trans.save()
        except:
            messages.error(request, 'An error occured saving resolved and new transactions.')
            return redirect(reverse('ledger:resolve'))
        rb = Running_Balance(account=off_acc, transaction=new_trans, value=off_acc.balance)
        rb1 = Running_Balance(account=acc, transaction=pre_auth_debit, value=acc.balance-total)
        rb2 = Running_Balance(account=acc, transaction=new_trans, value=acc.balance)
        rb.save()
        rb1.save()
        rb2.save()
        messages.success(request, 'Successfully resolved.')
        return redirect(reverse('ledger:adat_index'))

def custom_receipt(request, acc_id):
    if request.method == 'GET':
        try:
            acc = Account.objects.get(pk=acc_id)
        except:
            messages.warning(request, 'Could not find account details')
            return redirect(reverse('ledger:show_acc', args=(acc_id,)))

        context = {
            "acc": acc,
        }
        return render(request,'ledger/custom_receipt.html', context=context)

def uncleared(request):
    if request.method == 'GET':
        trans = Transaction.objects.filter(cleared=False)
        trans_list = [x for x in trans if x.receiver.is_office()]
        
        context = {
            'trans':trans_list,
        }
        return render(request, 'ledger/uncleared.html', context=context)
    else:
        trans_id = request.POST['trans_id']
        try:
            trans = Transaction.objects.get(pk = trans_id)
        except:
            messages.error(request, 'Unable to retrieve transaction with id: {trans_id}')
            return redirect(reverse('ledger:uncleared'))
        trans.cleared = True
        off_acc = trans.receiver
        off_acc.balance += trans.total
        new_rb = Running_Balance(account=off_acc, value = off_acc.balance, transaction = trans)
        try:
            trans.save()
        except:
            messages.error(request, 'Transaction failed to clear.')
            return redirect(reverse('ledger:uncleared'))
        try:
            new_rb.save()
        except:
            messages.error(request, 'Saving of running balance failed, but transaction cleared.')
            return redirect(reverse('ledger:uncleared'))
        try:
            off_acc.save()
        except:
            messages.error(request, 'Saving of office account balance failed, trans and r_b were saved.')
            return redirect(reverse('ledger:uncleared'))
        
        return redirect(reverse('ledger:uncleared'))

# search func on file no, name and client code.
def search(request):
    if request.method == "POST":
        search_q = request.POST['search_q']
        # an OR query to see if either NAME or FILE_NO field contain the searched string (case insensitive)
        accounts = Account.objects.filter(Q(file_no__icontains = search_q) | Q(name__icontains = search_q) | Q(client_code__icontains = search_q)).filter(client_account = True)
        return render(request, 'ledger/search.html', {'accs':accounts, 'search_q':search_q,})