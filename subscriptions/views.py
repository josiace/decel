from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import SubscriptionPlan, UserSubscription
from .services import SubscriptionService


@login_required
def subscription_plans(request):
    """Affiche les plans d'abonnement disponibles."""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order', 'dc_price')
    
    # Récupérer l'abonnement actif de l'utilisateur
    current_subscription = SubscriptionService.get_user_active_subscription(request.user)
    
    return render(request, 'subscriptions/plans.html', {
        'plans': plans,
        'current_subscription': current_subscription,
    })


@login_required
def subscribe(request, plan_id):
    """Souscrit à un plan d'abonnement."""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    if request.method == 'POST':
        success, message, subscription = SubscriptionService.create_subscription(
            user=request.user,
            plan_id=plan_id,
            payment_method='dc'
        )
        
        if success:
            messages.success(request, message)
            return redirect('subscription_detail', subscription_id=subscription.id)
        else:
            messages.error(request, message)
            return redirect('subscription_plans')
    
    return render(request, 'subscriptions/subscribe.html', {
        'plan': plan,
    })


@login_required
def subscription_detail(request, subscription_id):
    """Affiche les détails de l'abonnement de l'utilisateur."""
    subscription = get_object_or_404(UserSubscription, id=subscription_id, user=request.user)
    transactions = subscription.transactions.all()[:10]
    
    return render(request, 'subscriptions/detail.html', {
        'subscription': subscription,
        'transactions': transactions,
    })


@login_required
def my_subscription(request):
    """Affiche l'abonnement actuel de l'utilisateur."""
    subscription = SubscriptionService.get_user_active_subscription(request.user)
    
    if subscription:
        return redirect('subscription_detail', subscription_id=subscription.id)
    else:
        return redirect('subscription_plans')


@login_required
@require_POST
def cancel_subscription(request, subscription_id):
    """Annule l'abonnement de l'utilisateur."""
    subscription = get_object_or_404(UserSubscription, id=subscription_id, user=request.user)
    
    reason = request.POST.get('reason', '')
    success, message = SubscriptionService.cancel_subscription(subscription_id, reason)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('subscription_detail', subscription_id=subscription_id)


@login_required
def upgrade_subscription(request):
    """Upgrade l'abonnement de l'utilisateur."""
    current_subscription = SubscriptionService.get_user_active_subscription(request.user)
    
    if not current_subscription:
        messages.error(request, "Vous n'avez pas d'abonnement actif.")
        return redirect('subscription_plans')
    
    # Récupérer les plans plus chers
    available_plans = SubscriptionPlan.objects.filter(
        is_active=True,
        dc_price__gt=current_subscription.plan.dc_price
    ).order_by('dc_price')
    
    if request.method == 'POST':
        new_plan_id = request.POST.get('plan_id')
        success, message, subscription = SubscriptionService.upgrade_subscription(
            user=request.user,
            new_plan_id=new_plan_id
        )
        
        if success:
            messages.success(request, message)
            return redirect('subscription_detail', subscription_id=subscription.id)
        else:
            messages.error(request, message)
    
    return render(request, 'subscriptions/upgrade.html', {
        'current_subscription': current_subscription,
        'available_plans': available_plans,
    })
