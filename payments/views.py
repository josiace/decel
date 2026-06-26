import json
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.services import DCService, PromoCodeService
from .models import DCPack, DCPackOrder, RechargeCode
from .services import RechargeCodeService, ManualPaymentService, DCPackOrderService


def _get_stripe():
    """Initialise Stripe avec la clé secrète. Retourne None si non configuré."""
    key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    if not key or key.startswith('sk_test_YOUR'):
        return None
    stripe.api_key = key
    return stripe


# ---------------------------------------------------------------------------
# Page principale — liste des packs DC
# ---------------------------------------------------------------------------

@login_required
def packs(request):
    """Affiche les packs DC disponibles à l'achat."""
    available_packs = DCPack.objects.filter(is_active=True)
    stripe_configured = bool(
        getattr(settings, 'STRIPE_SECRET_KEY', '').startswith('sk_')
        and not getattr(settings, 'STRIPE_SECRET_KEY', '').startswith('sk_test_YOUR')
    )

    context = {
        'packs': available_packs,
        'stripe_public_key': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
        'stripe_configured': stripe_configured,
        'user_dc': request.user.dc_balance,
    }
    return render(request, 'payments/packs.html', context)


# ---------------------------------------------------------------------------
# Création de la session Stripe Checkout
# ---------------------------------------------------------------------------

@login_required
@require_POST
def create_checkout_session(request, pack_id):
    """
    Crée une session Stripe Checkout pour un pack DC.
    Redirige l'utilisateur vers la page de paiement Stripe.
    Supporte les codes promo.
    """
    pack = get_object_or_404(DCPack, id=pack_id, is_active=True)
    stripe_lib = _get_stripe()

    if not stripe_lib:
        messages.error(
            request,
            "Le système de paiement n'est pas encore configuré. "
            "Contactez l'administrateur."
        )
        return redirect('payments:packs')

    # Appliquer le code promo si fourni
    promo_code = request.POST.get('promo_code', '').strip()
    discount = 0
    if promo_code:
        success, message, discount_amount = PromoCodeService.apply_promo_code(request.user, promo_code)
        if success:
            discount = discount_amount
            messages.success(request, f"Code promo appliqué : -{discount} DC")
        else:
            messages.error(request, message)
            return redirect('payments:packs')

    # Calculer le prix après réduction
    base_price = pack.price_cfa if pack.price_cfa else 0
    final_price = max(0, base_price - discount)

    if final_price == 0:
        # Si le code promo rend le pack gratuit, créditer directement
        DCService.add_dc(
            user=request.user,
            amount=pack.dc_amount,
            transaction_type='purchase',
            description=f"Achat pack DC gratuit avec code promo : {pack.name}",
            content_type='dc_pack',
            content_id=pack.id
        )
        messages.success(request, f"Pack {pack.name} obtenu gratuitement grâce au code promo !")
        return redirect('payments:packs')

    try:
        success_url = request.build_absolute_uri(
            f'/payments/success/?session_id={{CHECKOUT_SESSION_ID}}'
        )
        cancel_url = request.build_absolute_uri('/payments/cancel/')

        session = stripe_lib.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'unit_amount': int(final_price * 100),  # Stripe utilise les centimes
                    'product_data': {
                        'name': f'DECEL — {pack.name}',
                        'description': f'{pack.dc_amount} Decelcones (DC)',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(request.user.id),
            metadata={
                'user_id': str(request.user.id),
                'pack_id': str(pack.id),
                'dc_amount': str(pack.dc_amount),
                'promo_code': promo_code,
                'discount': str(discount),
            },
            customer_email=request.user.email,
        )

        # Créer la commande en statut 'pending'
        DCPackOrder.objects.create(
            user=request.user,
            pack=pack,
            dc_amount=pack.dc_amount,
            price_paid_cfa=final_price,
            stripe_session_id=session.id,
        )

        return redirect(session.url, code=303)

    except stripe_lib.error.StripeError as e:
        messages.error(request, f"Erreur de paiement : {e.user_message}")
        return redirect('payments:packs')


# ---------------------------------------------------------------------------
# Page de succès après paiement
# ---------------------------------------------------------------------------

@login_required
def checkout_success(request):
    """
    Page de confirmation après un paiement réussi.
    Vérifie la session Stripe et crédite les DC si ce n'est pas déjà fait.
    """
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('payments:packs')

    stripe_lib = _get_stripe()

    try:
        order = DCPackOrder.objects.get(stripe_session_id=session_id, user=request.user)
    except DCPackOrder.DoesNotExist:
        messages.error(request, "Commande introuvable.")
        return redirect('payments:packs')

    # Éviter le double crédit (le webhook est la source principale)
    if order.status == 'completed':
        if DCPackOrderService.has_dc_credit(order):
            context = {'order': order, 'already_credited': True}
            return render(request, 'payments/checkout_success.html', context)

        success, message = DCPackOrderService.recredit_missing_order(order)
        if success:
            messages.success(request, f"✅ {message}")
        else:
            messages.error(request, message)
        order.refresh_from_db()
        context = {'order': order, 'already_credited': DCPackOrderService.has_dc_credit(order)}
        return render(request, 'payments/checkout_success.html', context)

    # Vérification Stripe si disponible
    if stripe_lib:
        try:
            session = stripe_lib.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                _complete_order(order)
        except stripe_lib.error.StripeError:
            pass
    else:
        # Mode dev sans Stripe : on crédite directement
        _complete_order(order)

    order.refresh_from_db()
    if DCPackOrderService.has_dc_credit(order):
        messages.success(
            request,
            f"✅ Paiement confirmé ! {order.dc_amount} DC ont été ajoutés à votre portefeuille."
        )
    else:
        messages.warning(
            request,
            "Paiement reçu mais les DC ne sont pas encore crédités. "
            "Contactez l'administrateur si le problème persiste."
        )
    context = {'order': order}
    return render(request, 'payments/checkout_success.html', context)


# ---------------------------------------------------------------------------
# Page d'annulation
# ---------------------------------------------------------------------------

@login_required
def checkout_cancel(request):
    """L'utilisateur a annulé le paiement sur Stripe."""
    messages.warning(request, "Paiement annulé. Votre solde DC n'a pas été modifié.")
    return render(request, 'payments/checkout_cancel.html')


# ---------------------------------------------------------------------------
# Webhook Stripe (source principale de confirmation)
# ---------------------------------------------------------------------------

@csrf_exempt
def stripe_webhook(request):
    """
    Reçoit les événements Stripe.
    C'est la source fiable pour créditer les DC — indépendant du navigateur.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    stripe_lib = _get_stripe()
    if not stripe_lib or not webhook_secret or webhook_secret.startswith('whsec_YOUR'):
        return HttpResponse(status=200)  # Ignorer si non configuré

    try:
        event = stripe_lib.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return HttpResponse("Payload invalide", status=400)
    except stripe_lib.error.SignatureVerificationError:
        return HttpResponse("Signature invalide", status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Abonnement ou achat one-time
        if session.get('metadata', {}).get('type') == 'subscription':
            _handle_subscription_activated(session)
        else:
            _handle_checkout_completed(session)

    elif event['type'] == 'customer.subscription.deleted':
        _handle_subscription_cancelled(event['data']['object'])

    elif event['type'] == 'checkout.session.expired':
        session_id = event['data']['object']['id']
        DCPackOrder.objects.filter(
            stripe_session_id=session_id,
            status='pending'
        ).update(status='failed')

    return HttpResponse(status=200)


# ---------------------------------------------------------------------------
# Abonnement Créateur Pro (Stripe Subscriptions)
# ---------------------------------------------------------------------------

PLAN_LABELS = {
    'pro': 'Créateur Pro — 5 €/mois',
    'academy': 'Académie — 20 €/mois',
}


@login_required
@require_POST
def create_subscription_session(request, plan):
    """
    Crée une session Stripe Checkout pour un abonnement contributeur.
    Le plan est 'pro' ou 'academy'.
    """
    if not request.user.is_contributor():
        messages.error(request, "Vous devez être contributeur pour souscrire à un plan.")
        return redirect('dashboard')

    if plan not in PLAN_LABELS:
        messages.error(request, "Plan invalide.")
        return redirect('contributor:pro_upgrade')

    stripe_lib = _get_stripe()
    price_id = getattr(settings, f'STRIPE_PRICE_{plan.upper()}', '')

    if not stripe_lib or not price_id:
        messages.error(
            request,
            f"L'abonnement {PLAN_LABELS[plan]} n'est pas encore configuré. "
            "Contactez l'administrateur."
        )
        return redirect('contributor:pro_upgrade')

    try:
        session = stripe_lib.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=request.build_absolute_uri('/payments/subscription/success/'),
            cancel_url=request.build_absolute_uri('/contributor/pro/'),
            client_reference_id=str(request.user.id),
            metadata={
                'user_id': str(request.user.id),
                'plan': plan,
                'type': 'subscription',
            },
            customer_email=request.user.email,
        )
        return redirect(session.url, code=303)

    except stripe_lib.error.StripeError as e:
        messages.error(request, f"Erreur de paiement : {e.user_message}")
        return redirect('contributor:pro_upgrade')


@login_required
def subscription_success(request):
    """Page de confirmation après activation d'un abonnement."""
    messages.success(
        request,
        "🎉 Abonnement activé ! Vos avantages Créateur Pro sont désormais disponibles."
    )
    return redirect('contributor:analytics')


# ---------------------------------------------------------------------------
# Helpers internes
# ---------------------------------------------------------------------------

def _handle_checkout_completed(session):
    """Traite un événement checkout.session.completed depuis le webhook."""
    try:
        order = DCPackOrder.objects.get(stripe_session_id=session['id'])
    except DCPackOrder.DoesNotExist:
        return

    if order.status == 'completed':
        return  # Déjà traité

    order.stripe_payment_intent = session.get('payment_intent', '')
    _complete_order(order)


def _handle_subscription_activated(session):
    """Active l'abonnement contributeur après paiement confirmé."""
    from datetime import timedelta
    from accounts.models import Contributor

    user_id = session.get('metadata', {}).get('user_id')
    plan = session.get('metadata', {}).get('plan', 'pro')
    subscription_id = session.get('subscription', '')

    if not user_id:
        return

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        contributor = Contributor.objects.get(user=user)
    except Exception:
        return

    contributor.plan = plan
    contributor.plan_expires_at = timezone.now() + timedelta(days=30)
    contributor.stripe_subscription_id = subscription_id or ''
    contributor.save(update_fields=['plan', 'plan_expires_at', 'stripe_subscription_id'])


def _handle_subscription_cancelled(subscription):
    """Réinitialise le plan du contributeur à 'free' après annulation."""
    from accounts.models import Contributor
    sub_id = subscription.get('id', '')
    if not sub_id:
        return
    Contributor.objects.filter(stripe_subscription_id=sub_id).update(
        plan='free',
        plan_expires_at=None,
        stripe_subscription_id='',
    )


def _complete_order(order: DCPackOrder):
    """
    Marque la commande comme complétée et crédite les DC.
    Atomique — appelé soit depuis le webhook, soit depuis la vue success.
    """
    DCPackOrderService.complete_order(
        order=order,
        transaction_type='purchase',
        description=f"Achat pack DC : {order.dc_amount} DC via Stripe",
    )


# ---------------------------------------------------------------------------
# Paiements alternatifs (sans API)
# ---------------------------------------------------------------------------

@login_required
def manual_payment(request, pack_id):
    """Affiche le formulaire de paiement manuel avec support des codes promo."""
    pack = get_object_or_404(DCPack, id=pack_id, is_active=True)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        transaction_reference = request.POST.get('transaction_reference', '').strip()
        promo_code = request.POST.get('promo_code', '').strip()
        
        if payment_method not in ['orange_money', 'wave', 'bank_transfer', 'cash']:
            messages.error(request, 'Méthode de paiement invalide.')
            return redirect('payments:packs')
        
        # Appliquer le code promo si fourni
        discount = 0
        if promo_code:
            success, message, discount_amount = PromoCodeService.apply_promo_code(request.user, promo_code)
            if success:
                discount = discount_amount
                messages.success(request, f"Code promo appliqué : -{discount} FCFA")
            else:
                messages.error(request, message)
        
        # Calculer le prix après réduction
        base_price = pack.price_cfa if pack.price_cfa else 0
        final_price = max(0, base_price - discount)
        
        # Créer la commande
        order = ManualPaymentService.create_manual_order(
            user=request.user,
            pack=pack,
            payment_method=payment_method,
            transaction_reference=transaction_reference,
            final_price=final_price
        )
        
        messages.success(request, f'Commande créée ! Veuillez effectuer le paiement via {payment_method}.')
        return redirect('payments:order_detail', order_id=order.id)
    
    context = {
        'pack': pack,
        'payment_methods': [
            ('orange_money', 'Orange Money'),
            ('wave', 'Wave'),
            ('bank_transfer', 'Virement bancaire'),
            ('cash', 'Espèces'),
        ],
        'payment_instructions': {
            'orange_money': 'Envoyez le montant au numéro Orange Money : +223 74 15 20 49. Contactez-nous sur WhatsApp pour confirmer.',
            'wave': 'Envoyez le montant au numéro Wave : +223 69 54 93 91. Contactez-nous sur WhatsApp pour confirmer.',
            'bank_transfer': 'Contactez-nous par email (afletounoudouprince5@gmail.com) ou WhatsApp (+223 69 54 93 91) pour les informations bancaires.',
            'cash': 'Contactez-nous par email (afletounoudouprince5@gmail.com) ou WhatsApp (+223 69 54 93 91) pour un paiement en espèces.',
        }
    }
    return render(request, 'payments/manual_payment.html', context)


@login_required
def order_detail(request, order_id):
    """Affiche les détails d'une commande."""
    order = get_object_or_404(DCPackOrder, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'payments/order_detail.html', context)


@login_required
def recharge_code(request):
    """Affiche le formulaire d'utilisation de code de recharge."""
    if request.method == 'POST':
        code_str = request.POST.get('code', '').strip().upper()
        
        success, message, transaction = RechargeCodeService.use_recharge_code(
            user=request.user,
            code_str=code_str
        )
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        
        return redirect('payments:wallet')
    
    return render(request, 'payments/recharge_code.html')


@login_required
def my_orders(request):
    """Affiche les commandes de l'utilisateur."""
    orders = DCPackOrder.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'payments/my_orders.html', context)
