from django.urls import path
from . import views

urlpatterns = [
    # Anasayfaya gidildiğinde views.py içindeki 'index' fonksiyonunu çalıştır
    path('', views.index, name='index'),
    path('bagaj/', views.bagaj_yonetimi, name='bagaj_sayfasi'),

    path('ucus-ara/', views.flight_search, name='flight_search'),

    path('ticket/', views.ticket_detail, name='ticket_page'),

    path('bilet/pdf/<int:ticket_id>/', views.ticket_pdf_view, name='ticket_pdf'),

    # Yeni eklenen bilet oluşturma yolu - NoReverseMatch hatasını çözer
    path('bilet-olustur/<int:flight_id>/', views.create_ticket, name='create_ticket'),

    # Bilet İptal Yolu
    path('bilet-iptal/<int:ticket_id>/', views.cancel_ticket, name='cancel_ticket'),

    # Akıllı Bagaj Takip Yolu
    path('bagaj-takip/<str:tag_number>/', views.baggage_track, name='baggage_track'),
]