from django.shortcuts import render
from django.utils import timezone

def home(request):
    context = {
        "now": timezone.now(),
    }
    return render(request, "index.html", context)

from django.shortcuts import render, redirect
from users.models import News
from django.contrib.admin.views.decorators import staff_member_required

def news_page(request):
    news = News.objects.all()

    if request.method == 'POST' and request.user.is_superuser:
        News.objects.create(
            title=request.POST['title'],
            text=request.POST['text']
        )
        return redirect('news')

    return render(request, 'news.html', {
        'news': news
    })

@staff_member_required
def news_delete(request, pk):
    News.objects.filter(pk=pk).delete()
    return redirect('news')

def contacts(request):
    return render(request, 'contacts.html')

