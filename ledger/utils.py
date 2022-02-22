from django.shortcuts import get_object_or_404, redirect
from .models import Account, Transaction
from django.urls import reverse
import json
from decimal import Decimal

def new_external(name):
    count = 0
    count += len(Account.objects.filter(file_no__startswith='EXTERNAL'))
    other_party = Account(name=name, file_no=f"EXTERNAL{count}", balance=0)
    other_party.save()
    return other_party


def redirect_to(acc_id):
    acc = get_object_or_404(Account, pk=acc_id)
    if acc.is_office():
        return redirect(reverse('ledger:show_off', args=(acc_id,)))
    else:
        return redirect(reverse('ledger:show_acc', args=(acc_id,)))


def json_prep(objects):
    new_list=[]
    for each in objects:
        new_list.append({
            'id':each.id,
            'created_at':each.created_at.strftime('%d/%m/%Y'),
            'receiver':each.receiver.name,
            'payee':each.payee.name,
            'table_list': json.loads(each.table_list),
            'total' : str(each.total),
            'category': each.category,
            'voucher_no': each.off_voucher_no,
        })
    return(json.dumps(new_list))

# removed after 1 time use
def categorize_ad():
    to_cat = [y for y in Transaction.objects.all() if y.payee.is_office()]
    for each in to_cat:
        tbl_list = json.loads(each.table_list)
        if tbl_list[0]['type_code'] == 'AD':
            each.category = 'AD'
            each.save()