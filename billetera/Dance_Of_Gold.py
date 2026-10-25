##	============ ##
##		GOLD	 ##
##	============ ##

# Vistas de la billetera institucional.

#	=== IMPORTS ===	#
from decimal import Decimal

from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from config.Door_To_The_Abyss import Saint_Germain
from usuarios.Divine_Bloodlines import Belmont_Blood_Only
from .Tribute import Hammer_Ledger
from .models import Hammer_Receipt


#	=== COUNTING ===	#

# "Hammer counts the coins without opening every purse."
def Hammer_Counts(Receipts):
    # Los totales los suma la base de datos, no Python fila por fila.
    return Receipts.aggregate(
        Ingresos=Sum('Monto', filter=Q(Tipo=Hammer_Receipt.Ingreso), default=Decimal('0')),
        Egresos=Sum('Monto', filter=Q(Tipo=Hammer_Receipt.Egreso), default=Decimal('0')),
    )


# "Only the receipts you asked about."
def Hammer_Sorts(request, Receipts):
    Tipo = request.GET.get('tipo', '')
    if Tipo in dict(Hammer_Receipt.Tipo_Choices):
        Receipts = Receipts.filter(Tipo=Tipo)
    elif Tipo not in dict(Hammer_Receipt.Tipo_Choices):
        Tipo = ''
    Busqueda = request.GET.get('q', '').strip()
    if Busqueda != '':
        Receipts = Receipts.filter(Concepto__icontains=Busqueda)
    return Receipts, Tipo, Busqueda


#	=== THE SHOP ===	#

# "What are ya buying? What are ya selling?"
@Belmont_Blood_Only
def Hammer(request):
    Totals = Hammer_Counts(Hammer_Receipt.objects.all())
    Receipts, Tipo, Busqueda = Hammer_Sorts(request, Hammer_Receipt.objects.select_related('Registrado_Por'))
    Door, Map = Saint_Germain(request, Receipts)
    return render(request, 'billetera/billetera_list.html', {
        'Door': Door,
        'Map': Map,
        'Tipo': Tipo,
        'Busqueda': Busqueda,
        'Ingresos': Totals['Ingresos'],
        'Egresos': Totals['Egresos'],
        'Saldo': Totals['Ingresos'] - Totals['Egresos'],
    })


# "Ring it up."
@Belmont_Blood_Only
@require_http_methods(['GET', 'POST'])
def Hammer_Rings_It_Up(request):
    Scroll = Hammer_Ledger(request.POST or None)
    if request.method == 'POST' and Scroll.is_valid() == True:
        Receipt = Scroll.save(commit=False)
        # El autor lo pone el servidor, nunca el formulario.
        Receipt.Registrado_Por = request.user
        Receipt.save()
        messages.success(request, f'{Receipt.Tipo} de ${Receipt.Monto:,.2f} registrado.')
        return redirect('Hammer')
    return render(request, 'billetera/movimiento_form.html', {'Scroll': Scroll, 'Titulo': 'Registrar movimiento'})
