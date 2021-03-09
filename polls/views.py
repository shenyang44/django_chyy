from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from .models import Question, Choice, Account
from django.urls import reverse
from django.views import generic
from django.utils import timezone

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_list'
    def get_queryset(self):
        return Account.objects.filter(updated_at__lte=timezone.now()).order_by('-updated_at')[:30]

class DetailView(generic.ListView):
    model = Account
    template_name='polls/detail.html'
    def get_queryset(self):
        return Transaction.objects.filter(account_id = 1)

def create_acc(request):
    if request.method == 'GET':
        return render(request, 'polls/create_acc.html')
    else:
        return redirect(reverse('polls:index'))


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
