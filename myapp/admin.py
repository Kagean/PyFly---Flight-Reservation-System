from django.contrib import admin
# Eski 'TodoItem' yerine yeni modellerini import ediyoruz
from .models import Airport, Aircraft, Personnel, Flight, Passenger, Ticket, Baggage

# Modelleri admin paneline kaydediyoruz
admin.site.register(Airport)
admin.site.register(Aircraft)
admin.site.register(Personnel)
admin.site.register(Flight)
admin.site.register(Passenger)
admin.site.register(Ticket)
admin.site.register(Baggage)