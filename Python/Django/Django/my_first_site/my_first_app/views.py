from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect
from django.urls import reverse

articles = {
    'sports':'Sports Page',
    'finance':'Finance Page',
    'politics':'Politics Page'
}

# Create your views here.
def index(request):
    return HttpResponse("Hello, this is a view inside my_app")

def news_view(request,topic):
    try:
        result = articles[topic]
        return HttpResponse(result)
    except:
        result = "No page for that topic!"
        raise Http404(result)

def add_view(request, num1, num2):
    result = num1 + num2
    return HttpResponse(str(result))

def num_page_view(request,num_page):
    topics_list = list(articles.keys())
    topic = topics_list[num_page]
    return HttpResponseRedirect(reverse('topic-page', args=[topic]))

def simple_view(request):
    return render(request, "first_app/example.html") # .html

def variable_view(request):
    my_var = {'first_name':'Rosaline','last_name':'Franklin',
              'some_list':[1,2,3],'some_dict':{'inside_key':'inside_value'},
              'user_logged_in':True
              }
    return render(request, 'first_app/example2.html', context=my_var)

def base_html(request):
    return render(request, "first_app/example-inherit.html")

