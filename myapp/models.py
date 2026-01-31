from django.db import models
import uuid  # PNR oluşturmak için
from django.utils import timezone


# --- ORTAK Abstract Model ---
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True

# --- SEÇENEK LİSTELERİ (ENUMS) ---
class UserRoles(models.TextChoices):
    PILOT = 'PILOT', 'Pilot'
    CABIN_CREW = 'CREW', 'Kabin Ekibi'
    OPERATIONS = 'OPS', 'Operasyon Personeli'

class FlightStatus(models.TextChoices):
    SCHEDULED = 'SCH', 'Zamanında'
    DELAYED = 'DLY', 'Rötarlı'
    CANCELLED = 'CNL', 'İptal Edildi'
    COMPLETED = 'CMP', 'Tamamlandı'

class BaggageStatus(models.TextChoices):
    CHECKED = 'CHECKED', 'Teslim Alındı'
    LOADED = 'LOADED', 'Uçağa Yüklendi'
    DELIVERED = 'DELIVERED', 'Yolcuya Teslim Edildi'
    LOST = 'LOST', 'Kayıp'

# --- MODELLER ---

class Airport(TimeStampedModel):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Aircraft(TimeStampedModel):
    tail_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=50)
    capacity_economy = models.IntegerField(default=180)
    capacity_business = models.IntegerField(default=20)

    def __str__(self):
        return f"{self.tail_number} ({self.model})"

class Personnel(TimeStampedModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=10, choices=UserRoles.choices)
    
    def __str__(self):
        return f"{self.get_role_display()} - {self.first_name} {self.last_name}"

class Flight(TimeStampedModel):
    flight_number = models.CharField(max_length=10, unique=True)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departures')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arrivals')
    gate = models.CharField(max_length=10, default="B12", verbose_name="Kapı Numarası")
    aircraft = models.ForeignKey(Aircraft, on_delete=models.SET_NULL, null=True)
    
    # base_price alanı 'price' olarak güncellendi
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    departure_time = models.DateTimeField(null=True, blank=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=3, choices=FlightStatus.choices, default=FlightStatus.SCHEDULED)
    crew = models.ManyToManyField(Personnel, related_name='flights')

    def get_duration(self):
        if self.arrival_time and self.departure_time:
            duration = self.arrival_time - self.departure_time
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}s {minutes}d"
        return "N/A"

    def __str__(self):
        return f"{self.flight_number}: {self.origin.code} -> {self.destination.code}"

class Passenger(TimeStampedModel):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    passport_number = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Ticket(TimeStampedModel):
    pnr = models.CharField(max_length=6, unique=True, editable=False)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='tickets')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='tickets')
    seat_number = models.CharField(max_length=5)
    is_checked_in = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.pnr:
            self.pnr = str(uuid.uuid4()).upper()[:6]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PNR: {self.pnr} - {self.flight.flight_number}"
    
    class Meta:
        unique_together = ('flight', 'seat_number')

class Baggage(TimeStampedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='baggages')
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=BaggageStatus.choices, default=BaggageStatus.CHECKED)
    extra_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tag_number = models.CharField(max_length=20, unique=True)

    def calculate_extra_fee(self):
        limit = 20.0
        rate_per_kg = 50.0
        if float(self.weight) > limit:
            self.extra_fee = (float(self.weight) - limit) * rate_per_kg
        else:
            self.extra_fee = 0.0
        self.save()

    def __str__(self):
        return f"Tag: {self.tag_number} - {self.ticket.passenger}"