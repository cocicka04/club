from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Tariff

def tariff_list(request):
    tariffs = Tariff.objects.all()

    if request.method == 'POST' and request.user.is_superuser:
        tariff = get_object_or_404(Tariff, id=request.POST.get('tariff_id'))
        tariff.name = request.POST.get('name')
        tariff.price_per_hour = request.POST.get('price_per_hour')
        tariff.description = request.POST.get('description')
        tariff.save()
        return redirect('tariffs:list')

    return render(request, 'tariffs/list.html', {
        'tariffs': tariffs
    })


@staff_member_required
def tariff_delete(request, pk):
    Tariff.objects.filter(pk=pk).delete()
    return redirect('tariffs:list')
