from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Tariff
from .forms import TariffForm
from .models import Category
from .forms import CategoryForm

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


@staff_member_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'tariffs/category_list.html', {'categories': categories})

@staff_member_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tariffs:category_list')
    else:
        form = CategoryForm()
    return render(request, 'tariffs/category_form.html', {'form': form, 'title': 'Новая категория'})

@staff_member_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('tariffs:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'tariffs/category_form.html', {'form': form, 'title': 'Редактирование категории'})

@staff_member_required
def category_delete(request, pk):
    Category.objects.filter(pk=pk).delete()
    return redirect('tariffs:category_list')