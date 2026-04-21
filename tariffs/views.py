from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Tariff
from .forms import TariffForm

def index(request):
    """Главная страница — теперь здесь ВСЕ тарифы в карусели"""
    tariffs = Tariff.objects.select_related('category').order_by('-id')
    return render(request, 'index.html', {
        'tariffs': tariffs
    })

@staff_member_required
def tariff_create(request):
    if request.method == 'POST':
        form = TariffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tariffs:index')
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
            return redirect('tariffs:index')
    else:
        form = TariffForm(instance=tariff)

    return render(request, 'tariffs/form.html', {
        'form': form,
        'title': 'Редактирование тарифа'
    })

@staff_member_required
def tariff_delete(request, pk):
    Tariff.objects.filter(pk=pk).delete()
    return redirect('tariffs:index')