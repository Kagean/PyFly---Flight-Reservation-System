from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.db.models import F, ExpressionWrapper, fields # Sıralama ve süre hesabı için şart
from io import BytesIO
from xhtml2pdf import pisa
import random 

# Modellerin import listesi
from .models import Ticket, Airport, Flight, Passenger, Baggage 

# --- Ana Sayfa ---
def index(request):
    return render(request, 'desktop.html')

# --- Bagaj Yönetimi (Orijinal Mantık Korundu) ---
def bagaj_yonetimi(request):
    pnr_from_url = request.GET.get('pnr', '')
    context = {'pnr_from_url': pnr_from_url}
    
    if request.method == "POST":
        ticket_pnr = request.POST.get('ticketNumber')
        weight = request.POST.get('weight')
        
        try:
            ticket = Ticket.objects.get(pnr=ticket_pnr)
            tag_no = f"PY-{random.randint(100000, 999999)}"
            
            baggage, created = Baggage.objects.update_or_create(
                ticket=ticket,
                defaults={
                    'weight': weight,
                    'tag_number': tag_no,
                    'status': 'CHECKED'
                }
            )
            
            baggage.calculate_extra_fee()
            
            context.update({
                'baggage_data': {
                    'ticket_number': ticket_pnr,
                    'weight': weight,
                    'extra_fee': baggage.extra_fee
                },
                'current_status': 2,
                'progress_percentage': 50,
                'success_message': "Bagaj kaydınız ve ücret hesaplaması tamamlandı."
            })
        except Ticket.DoesNotExist:
            context['error_message'] = "Hata: Geçersiz bilet numarası."
            
    return render(request, 'Bagaj.html', context)

# --- Uçuş Arama (Dinamik Filtreleme ve Sıralama Entegre Hali) ---
def flight_search(request):
    airports = Airport.objects.all().order_by('city')
    passenger_count = int(request.GET.get('passengers', 1))
    
    # Parametreleri al
    origin_id = request.GET.get('origin')
    destination_id = request.GET.get('destination')
    departure_date = request.GET.get('departure_date')
    max_price = request.GET.get('price') # Slider'dan gelen fiyat
    sort_by = request.GET.get('sort')    # Butonlardan gelen sıralama tipi

    flights = Flight.objects.all().select_related('origin', 'destination')

    # 1. Filtreleri Uygula
    if origin_id and origin_id.strip():
        flights = flights.filter(origin_id=origin_id)
    if destination_id and destination_id.strip():
        flights = flights.filter(destination_id=destination_id)
    if departure_date and departure_date.strip():
        flights = flights.filter(departure_time__date=departure_date)
    if max_price:
        flights = flights.filter(price__lte=max_price)

    # 2. SIRALAMA MANTIĞI
    if sort_by == 'price':
        # En Uygun Fiyat: En ucuzdan pahalıya doğru
        flights = flights.order_by('price')
    elif sort_by == 'departure':
        # En Erken Kalkış: Saati en erken olan en yukarıda
        flights = flights.order_by('departure_time')
    elif sort_by == 'duration':
        # En Kısa Süre: Varış - Kalkış farkını hesapla ve sırala
        flights = flights.annotate(
            duration_val=ExpressionWrapper(
                F('arrival_time') - F('departure_time'), 
                output_field=fields.DurationField()
            )
        ).order_by('duration_val')
    else:
        # Varsayılan: Fiyata göre sırala
        flights = flights.order_by('price')

    # 3. Toplam Fiyat Hesapla
    for flight in flights:
        flight.total_price = flight.price * passenger_count

    # 4. AJAX Kontrolü (Dinamik güncelleme için)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = []
        for f in flights:
            data.append({
                'id': f.id,
                'airline': f.airline,
                'flight_number': f.flight_number,
                'departure': f.departure_time.strftime('%H:%M'),
                'arrival': f.arrival_time.strftime('%H:%M'),
                'origin_code': f.origin.code,
                'dest_code': f.destination.code,
                'price': float(f.price),
                'total_price': float(f.total_price),
                'duration': f.get_duration() if hasattr(f, 'get_duration') else "1s 30dk"
            })
        return JsonResponse({'flights': data})

    context = {
        'airports': airports,
        'flights': flights,
        'passenger_count': passenger_count,
    }
    return render(request, 'flights.html', context)

# --- Bilet Oluşturma (Orijinal Mantık Korundu) ---
def create_ticket(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    passenger = Passenger.objects.first() # Demo için ilk yolcuyu alıyoruz
    
    if not passenger:
        return HttpResponse("Hata: Veritabanında kayıtlı yolcu bulunamadı.")

    passenger_count = int(request.GET.get('passengers', 1))

    def generate_random_seat():
        row = random.randint(1, 30)
        letter = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
        return f"{row}{letter}"

    for _ in range(passenger_count):
        seat = generate_random_seat()
        while Ticket.objects.filter(flight=flight, seat_number=seat).exists():
            seat = generate_random_seat()

        Ticket.objects.create(
            passenger=passenger,
            flight=flight,
            seat_number=seat, 
            price=flight.price
        )
    
    return redirect('ticket_page')

# --- Diğer Fonksiyonlar (Aynen Korundu) ---
def ticket_detail(request):
    tickets = Ticket.objects.all().select_related('flight__origin', 'flight__destination', 'passenger')
    return render(request, 'Ticket.html', {'tickets': tickets})

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    return result.getvalue() if not pdf.err else None

def ticket_pdf_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    context = {'tickets': [ticket], 'is_pdf': True}
    pdf = render_to_pdf('Ticket.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"PyFly_Fatura_{ticket.pnr}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return HttpResponse("PDF oluşturulurken bir hata oluştu.", status=404)

def cancel_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.delete()
    return redirect('ticket_page')

def baggage_track(request, tag_number):
    baggage = get_object_or_404(Baggage, tag_number=tag_number)
    status_map = {'CHECKED': 25, 'LOADED': 50, 'IN_FLIGHT': 75, 'ARRIVED': 100}
    progress = status_map.get(baggage.status, 0)
    
    context = {
        'baggage': baggage,
        'progress_percentage': progress,
        'is_tracking_view': True
    }
    return render(request, 'Baggage_Track.html', context)