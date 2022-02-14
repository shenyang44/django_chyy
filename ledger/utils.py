from .models import Account
def new_external(name):
    count = 0
    count += len(Account.objects.filter(file_no__startswith='EXTERNAL'))
    other_party = Account(name=name, file_no=f"EXTERNAL{count}", balance=0)
    other_party.save()
    return other_party