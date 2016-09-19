from django.contrib.auth.forms import AuthenticationForm
from django.http import Http404
from django.shortcuts import render, get_object_or_404

from .models import Question, Solution
from .models import search_alg
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import UserForm


# Create your views here.
def index(request):

    #Taking care of the 404 error
    try:
        questions_list = Question.objects.order_by('title')
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    languages = Solution.LANGUAGE
    difficulty = Question.DIFFICULTY

    all_tags = []
    for question in questions_list:
        for tag in question.tags.all():
            if tag not in all_tags:
                all_tags.append(tag)

    context = {
        'question_list': questions_list,
        'languages': languages,
        'difficulty': difficulty,
        'tag_list': all_tags
    }

    # This is a shortcut and saves having to use the loader class
    return render(request, "problemfinder/index.html", context)


def search(request):
    #Taking care of the 404 error
    try:
        questions_list = Question.objects.filter(visible=True).order_by('title')
    except Question.DoesNotExist:
        raise Http404("Question does not exist")

    languages = Solution.LANGUAGE
    difficulty = Question.DIFFICULTY

    query = ''

    if ('q' in request.GET) and request.GET['q'].strip():
        query = request.GET['q']

    lan = request.GET.get('language', '----')
    difft = request.GET.get('difficulty', '----')

    if difft == "Difficulty" or difft == "----":
        difft = "Not Selected"

    if lan == "Language" or lan == "----":
        lan = "Not Selected"


    new_question_list = []
    searchResult = search_alg(query, questions_list, lan, difft)

    if searchResult == questions_list:
        new_question_list = searchResult
    else:
        if isinstance(searchResult, list):
            for result in searchResult:
                new_question_list.append(result)

    all_tags = []
    for question in questions_list:
        for tag in question.tags.all:
            if tag not in all_tags:
                all_tags.append(tag)



    context = {
        'question_list': new_question_list,
        'query': query,
        'languages': languages,
        'difficulty': difficulty,
        'languagesel': lan,
        'difft': difft,
        'tag_list': all_tags,
    }

    # This is a shortcut and saves having to use the loader class
    return render(request, "problemfinder/search.html", context)



class UserFormView(View):
    form_class = UserForm
    template_name = 'problemfinder/login.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():

            user = form.save(commit=False)

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(username+' : '+password   )
            user.set.password(password)
            user.save()

            user = authenticate(username=username, password=password)
            print(user)
            if user is not None:
                print(user)
                if user.is_active:
                    login(request, user)
                    return redirect('ProblemFinder:index')
        else:
            print("form invalid")
            print(form.errors)

        return render(request, "problemfinder/login.html")

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'problemfinder/details.html', {'question': question})
