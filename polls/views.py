from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from .models import Question, Choice, Account, Transaction
from django.urls import reverse
from django.views import generic
from django.utils import timezone

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_list'
    def get_queryset(self):
        return Account.objects.filter(created_at__lte=timezone.now())

class DetailView(generic.ListView):
    model = Account
    template_name='polls/detail.html'
    def get_queryset(self):
        return Transaction.objects.filter(account_id = self.kwargs['pk'])

def show_acc(request, acc_id):
    account = get_object_or_404(Account, pk=acc_id)
    transactions = Transaction.objects.filter(account_id = acc_id)
    context={
        'account':account,
        'transactions':transactions
    }
    return render(request, 'polls/show-acc.html', context=context)

def create_acc(request):
    if request.method == 'GET':
        return render(request, 'polls/create_acc.html')
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
            return render(request, 'polls/create_acc.html', {
                'error_message' : "Error encountered in saving the account failed.",
            })
            
        return redirect(reverse('polls:index'))

def create_trans(request, acc_id):
    if request.method == 'POST':
        trans_type = request.POST['trans_type']
        amount = request.POST['amount']
        account = get_object_or_404(Account, pk=request.POST['acc_id'])
        if trans_type == 'received':
            received = True
        else:
            received = False
        
        try:
            # new_trans = account.transaction_set.create(received=received, amount=amount)
            print(x)
        except:
            return render(request, 'polls/transaction.html', {'account':account, 'error_message':'Saving the new transaction failed for:'})

        return redirect(reverse('polls:create_trans', args=[acc_id]))
        
    else:
        account = get_object_or_404(Account, pk=acc_id)
        return render(request, 'polls/transaction.html', {'account':account})

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
