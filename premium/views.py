from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import PremiumService, PremiumBooking
from .services import PremiumServiceManager


@login_required
def service_list(request):
    """Affiche la liste des services premium disponibles."""
    subject_id = request.GET.get('subject')
    service_type = request.GET.get('service_type')
    
    services = PremiumServiceManager.get_available_services(
        subject=subject_id,
        service_type=service_type
    )
    
    from skills.models import Subject
    subjects = Subject.objects.all()
    
    return render(request, 'premium/service_list.html', {
        'services': services,
        'subjects': subjects,
    })


@login_required
def service_detail(request, service_id):
    """Affiche les détails d'un service premium."""
    service = get_object_or_404(PremiumService, id=service_id, status='active')
    
    # Récupérer les avis
    reviews = service.reviews.select_related('reviewer').order_by('-created_at')[:10]
    
    return render(request, 'premium/service_detail.html', {
        'service': service,
        'reviews': reviews,
    })


@login_required
def book_service(request, service_id):
    """Réserve un service premium."""
    service = get_object_or_404(PremiumService, id=service_id, status='active')
    
    if request.method == 'POST':
        scheduled_date = request.POST.get('scheduled_date')
        scheduled_time = request.POST.get('scheduled_time')
        
        from datetime import datetime
        scheduled_date = datetime.strptime(scheduled_date, '%Y-%m-%d').date()
        scheduled_time = datetime.strptime(scheduled_time, '%H:%M').time()
        
        success, message, booking = PremiumServiceManager.book_service(
            student=request.user,
            service_id=service_id,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time
        )
        
        if success:
            messages.success(request, message)
            return redirect('premium:booking_detail', booking_id=booking.id)
        else:
            messages.error(request, message)
    
    return render(request, 'premium/book_service.html', {
        'service': service,
    })


@login_required
def booking_detail(request, booking_id):
    """Affiche les détails d'une réservation."""
    booking = get_object_or_404(PremiumBooking, id=booking_id)
    
    # Vérifier que l'utilisateur a le droit de voir cette réservation
    if booking.student != request.user and booking.provider != request.user:
        messages.error(request, "Vous n'avez pas le droit de voir cette réservation.")
        return redirect('premium:my_bookings')
    
    return render(request, 'premium/booking_detail.html', {
        'booking': booking,
    })


@login_required
def my_bookings(request):
    """Affiche les réservations de l'utilisateur."""
    if request.user.is_contributor():
        bookings = PremiumServiceManager.get_provider_bookings(request.user)
    else:
        bookings = PremiumServiceManager.get_student_bookings(request.user)
    
    return render(request, 'premium/my_bookings.html', {
        'bookings': bookings,
    })


@login_required
def my_services(request):
    """Affiche les services créés par l'utilisateur (contributeur)."""
    if not request.user.is_contributor():
        messages.error(request, "Vous devez être contributeur pour créer des services.")
        return redirect('dashboard')
    
    services = PremiumServiceManager.get_provider_services(request.user)
    
    return render(request, 'premium/my_services.html', {
        'services': services,
    })


@login_required
def create_service(request):
    """Crée un nouveau service premium (contributeur)."""
    if not request.user.is_contributor():
        messages.error(request, "Vous devez être contributeur pour créer des services.")
        return redirect('dashboard')
    
    from skills.models import Subject
    subjects = Subject.objects.all()
    
    if request.method == 'POST':
        service_data = {
            'service_type': request.POST.get('service_type'),
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
            'subject_id': request.POST.get('subject'),
            'dc_price_per_hour': int(request.POST.get('dc_price_per_hour')),
            'dc_price_per_session': int(request.POST.get('dc_price_per_session')) if request.POST.get('dc_price_per_session') else None,
            'duration_minutes': int(request.POST.get('duration_minutes')),
            'is_online': request.POST.get('is_online') == 'on',
            'location': request.POST.get('location', ''),
            'requirements': request.POST.get('requirements', ''),
            'max_students_per_session': int(request.POST.get('max_students_per_session')),
            'available_days': request.POST.getlist('available_days'),
            'available_time_start': request.POST.get('available_time_start'),
            'available_time_end': request.POST.get('available_time_end'),
            'status': 'draft',
        }
        
        service = PremiumServiceManager.create_service(request.user, service_data)
        messages.success(request, "Service créé avec succès !")
        return redirect('premium:service_detail', service_id=service.id)
    
    return render(request, 'premium/create_service.html', {
        'subjects': subjects,
    })


@login_required
@require_POST
def confirm_booking(request, booking_id):
    """Confirme une réservation (prestataire)."""
    booking = get_object_or_404(PremiumBooking, id=booking_id, provider=request.user)
    
    success, message = PremiumServiceManager.confirm_booking(booking_id)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('premium:booking_detail', booking_id=booking_id)


@login_required
@require_POST
def start_session(request, booking_id):
    """Démarre une session (prestataire)."""
    booking = get_object_or_404(PremiumBooking, id=booking_id, provider=request.user)
    
    meeting_link = request.POST.get('meeting_link', '')
    success, message = PremiumServiceManager.start_session(booking_id, meeting_link)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('premium:booking_detail', booking_id=booking_id)


@login_required
@require_POST
def complete_session(request, booking_id):
    """Termine une session (prestataire)."""
    booking = get_object_or_404(PremiumBooking, id=booking_id, provider=request.user)
    
    notes = request.POST.get('notes', '')
    success, message = PremiumServiceManager.complete_session(booking_id, notes)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('premium:booking_detail', booking_id=booking_id)


@login_required
@require_POST
def cancel_booking(request, booking_id):
    """Annule une réservation."""
    booking = get_object_or_404(PremiumBooking, id=booking_id)
    
    # Vérifier que l'utilisateur a le droit d'annuler
    if booking.student != request.user and booking.provider != request.user:
        messages.error(request, "Vous n'avez pas le droit d'annuler cette réservation.")
        return redirect('premium:booking_detail', booking_id=booking_id)
    
    reason = request.POST.get('reason', '')
    success, message = PremiumServiceManager.cancel_booking(booking_id, reason, request.user)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('premium:booking_detail', booking_id=booking_id)


@login_required
@require_POST
def submit_review(request, booking_id):
    """Soumet un avis sur une session."""
    booking = get_object_or_404(PremiumBooking, id=booking_id, student=request.user)
    
    review_data = {
        'rating': int(request.POST.get('rating')),
        'communication': int(request.POST.get('communication')),
        'expertise': int(request.POST.get('expertise')),
        'helpfulness': int(request.POST.get('helpfulness')),
        'punctuality': int(request.POST.get('punctuality')),
        'comment': request.POST.get('comment'),
    }
    
    success, message, review = PremiumServiceManager.submit_review(booking_id, review_data)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('premium:booking_detail', booking_id=booking_id)
