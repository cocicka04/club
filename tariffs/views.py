from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Tariff
from .forms import TariffForm
from django.core.paginator import Paginator

def index(request):
    tariffs = Tariff.objects.select_related('category').order_by('-id')

    return render(request, 'index.html', {
        'tariffs': tariffs
    })

def tariff_list(request):
    tariffs = Tariff.objects.all()

    paginator = Paginator(tariffs, 6)
    page_number = request.GET.get('page')
    tariffs = paginator.get_page(page_number)

    if request.method == 'POST' and request.user.is_superuser:
        tariff = get_object_or_404(Tariff, id=request.POST.get('tariff_id'))
        tariff.name = request.POST.get('name')
        tariff.price_per_hour = request.POST.get('price_per_hour')
        tariff.description = request.POST.get('description')
        tariff.save()
        return redirect('index')

    return render(request, 'tariffs/list.html', {
        'tariffs': tariffs
    })

@staff_member_required
def tariff_create(request):
    if request.method == 'POST':
        form = TariffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = TariffForm()

    return render(request, 'tariffs/form.html', {
        'form': form
    })

@staff_member_required
def tariff_edit(request, pk):
    tariff = get_object_or_404(Tariff, pk=pk)

    if request.method == 'POST':
        form = TariffForm(request.POST, instance=tariff)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = TariffForm(instance=tariff)

    return render(request, 'tariffs/form.html', {
        'form': form,
        'tariff': tariff,
        'title': 'Редактирование тарифа'
    })


@staff_member_required
def tariff_delete(request, pk):
    Tariff.objects.filter(pk=pk).delete()
    return redirect('index')
