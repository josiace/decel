from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import B2BPartner, B2BLicense, B2BUser
from .services import B2BService


def is_admin(user):
    """Check if user is admin."""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def partner_list(request):
    """Affiche la liste des partenaires B2B."""
    partners = B2BPartner.objects.all().order_by('-created_at')
    return render(request, 'b2b/partner_list.html', {'partners': partners})


@login_required
@user_passes_test(is_admin)
def partner_detail(request, partner_id):
    """Affiche les détails d'un partenaire."""
    partner = get_object_or_404(B2BPartner, id=partner_id)
    licenses = B2BService.get_partner_licenses(partner_id)
    transactions = partner.transactions.all()[:10]
    
    return render(request, 'b2b/partner_detail.html', {
        'partner': partner,
        'licenses': licenses,
        'transactions': transactions,
    })


@login_required
@user_passes_test(is_admin)
def create_partner(request):
    """Crée un nouveau partenaire B2B."""
    if request.method == 'POST':
        partner_data = {
            'name': request.POST.get('name'),
            'partner_type': request.POST.get('partner_type'),
            'contact_person': request.POST.get('contact_person'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone', ''),
            'address': request.POST.get('address', ''),
            'tax_id': request.POST.get('tax_id', ''),
            'registration_number': request.POST.get('registration_number', ''),
            'billing_email': request.POST.get('billing_email', ''),
            'billing_address': request.POST.get('billing_address', ''),
            'notes': request.POST.get('notes', ''),
            'status': 'pending',
        }
        
        partner = B2BService.create_partner(partner_data)
        messages.success(request, "Partenaire créé avec succès !")
        return redirect('b2b:partner_detail', partner_id=partner.id)
    
    return render(request, 'b2b/create_partner.html')


@login_required
@user_passes_test(is_admin)
def license_list(request):
    """Affiche la liste des licences B2B."""
    licenses = B2BLicense.objects.select_related('partner').all().order_by('-created_at')
    return render(request, 'b2b/license_list.html', {'licenses': licenses})


@login_required
@user_passes_test(is_admin)
def license_detail(request, license_id):
    """Affiche les détails d'une licence."""
    license = get_object_or_404(B2BLicense, id=license_id)
    users = B2BService.get_license_users(license_id)
    transactions = license.transactions.all()[:10]
    limits = B2BService.check_license_limits(license_id)
    
    return render(request, 'b2b/license_detail.html', {
        'license': license,
        'users': users,
        'transactions': transactions,
        'limits': limits,
    })


@login_required
@user_passes_test(is_admin)
def create_license(request, partner_id):
    """Crée une nouvelle licence pour un partenaire."""
    partner = get_object_or_404(B2BPartner, id=partner_id)
    
    if request.method == 'POST':
        from datetime import datetime
        
        license_data = {
            'license_type': request.POST.get('license_type'),
            'name': request.POST.get('name'),
            'description': request.POST.get('description', ''),
            'price_cfa': request.POST.get('price_cfa'),
            'billing_cycle': request.POST.get('billing_cycle'),
            'max_students': request.POST.get('max_students'),
            'max_teachers': request.POST.get('max_teachers'),
            'max_courses': request.POST.get('max_courses') or None,
            'max_exams': request.POST.get('max_exams') or None,
            'has_certificates': request.POST.get('has_certificates') == 'on',
            'has_analytics': request.POST.get('has_analytics') == 'on',
            'has_api_access': request.POST.get('has_api_access') == 'on',
            'has_custom_branding': request.POST.get('has_custom_branding') == 'on',
            'has_priority_support': request.POST.get('has_priority_support') == 'on',
            'start_date': datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date(),
            'end_date': datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').date(),
            'status': 'active',
        }
        
        license = B2BService.create_license(partner_id, license_data)
        messages.success(request, "Licence créée avec succès !")
        return redirect('b2b:license_detail', license_id=license.id)
    
    return render(request, 'b2b/create_license.html', {'partner': partner})


@login_required
@user_passes_test(is_admin)
@require_POST
def add_user_to_license(request, license_id):
    """Ajoute un utilisateur à une licence."""
    license = get_object_or_404(B2BLicense, id=license_id)
    
    user_id = request.POST.get('user_id')
    role = request.POST.get('role')
    
    success, message, b2b_user = B2BService.add_user_to_license(
        license_id=license_id,
        user_id=user_id,
        role=role,
        added_by=request.user
    )
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('b2b:license_detail', license_id=license_id)


@login_required
@user_passes_test(is_admin)
@require_POST
def remove_user_from_license(request, license_id, user_id):
    """Retire un utilisateur d'une licence."""
    success, message = B2BService.remove_user_from_license(license_id, user_id)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('b2b:license_detail', license_id=license_id)


@login_required
@user_passes_test(is_admin)
@require_POST
def renew_license(request, license_id):
    """Renouvelle une licence."""
    from datetime import datetime
    new_end_date = datetime.strptime(request.POST.get('new_end_date'), '%Y-%m-%d').date()
    
    success, message = B2BService.renew_license(license_id, new_end_date)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('b2b:license_detail', license_id=license_id)


@login_required
@user_passes_test(is_admin)
@require_POST
def upgrade_license(request, license_id):
    """Upgrade une licence avec des places supplémentaires."""
    additional_seats = int(request.POST.get('additional_seats'))
    
    success, message = B2BService.upgrade_license(license_id, additional_seats)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('b2b:license_detail', license_id=license_id)
