from .models import Account
def new_external(name):
    count = 0
    count += len(Account.objects.filter(file_no__startswith='EXTERNAL'))
    other_party = Account(name=name, file_no=f"EXTERNAL{count}", balance=0)
    other_party.save()
    return other_party

# removed after 1 time use
def categorize_ad():
    to_cat = [y for y in Transaction.objects.all() if y.payee.is_office()]
    for each in to_cat:
        tbl_list = json.loads(each.table_list)
        if tbl_list[0]['type_code'] == 'AD':
            each.category = 'AD'
            each.save()