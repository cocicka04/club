from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from users.models import News
from django.core.paginator import Paginator
from tariffs.models import Tariff

def home(request):
    tariffs = Tariff.objects.select_related('category').order_by('-id')

    context = {
        "now": timezone.now(),
        "tariffs": tariffs
    }

    return render(request, "index.html", context)

def news_page(request):
    news = News.objects.all()  

    paginator = Paginator(news, 5) 
    page_number = request.GET.get('page')
    news = paginator.get_page(page_number)


    if request.method == 'POST' and request.user.is_superuser:

        # СОЗДАНИЕ
        if 'create' in request.POST:
            News.objects.create(
                title=request.POST.get('title', '')[:120],
                text=request.POST.get('text', '')[:1000]
            )
            return redirect('news')

        # РЕДАКТИРОВАНИЕ
        if 'edit' in request.POST:
            item = get_object_or_404(News, pk=request.POST.get('news_id'))
            item.title = request.POST.get('title', '')[:120]
            item.text = request.POST.get('text', '')[:1000]
            item.save()
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

def about(request):
    return render(request, 'about.html')

