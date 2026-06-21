"""
Tests des vues HTTP — codes de statut, redirections, authentification requise.
Couvre : register, login, dashboard, wallet, streak_shield, payments/packs.
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from accounts.models import User, DCTransaction
from accounts.services import DCService
from payments.models import DCPack


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
def make_user(email='viewtest@test.com', dc_balance=50, **kwargs):
    return User.objects.create_user(
        username=email.split('@')[0],
        email=email,
        password='testpass123',
        first_name='View',
        last_name='Test',
        dc_balance=dc_balance,
        **kwargs,
    )


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class PublicViewTest(TestCase):
    """Vues accessibles sans authentification."""

    def test_home_returns_200(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_returns_200(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_returns_200(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class AuthRequiredViewTest(TestCase):
    """Vues qui redirigent vers login si non authentifié."""

    def test_dashboard_redirects_anonymous(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")

    def test_wallet_redirects_anonymous(self):
        response = self.client.get(reverse('wallet'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('wallet')}")

    def test_packs_redirects_anonymous(self):
        response = self.client.get(reverse('payments:packs'))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('payments:packs')}"
        )


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class DashboardViewTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.client.login(username=self.user.email, password='testpass123')

    def test_dashboard_returns_200(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_uses_correct_template(self):
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'accounts/dashboard.html')

    def test_dashboard_contains_user_data(self):
        response = self.client.get(reverse('dashboard'))
        self.assertIn('user_skills', response.context)
        self.assertIn('recommendations', response.context)
        self.assertIn('level_progress', response.context)


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class WalletViewTest(TestCase):

    def setUp(self):
        self.user = make_user(dc_balance=100)
        self.client.login(username=self.user.email, password='testpass123')

    def test_wallet_returns_200(self):
        response = self.client.get(reverse('wallet'))
        self.assertEqual(response.status_code, 200)

    def test_wallet_uses_correct_template(self):
        response = self.client.get(reverse('wallet'))
        self.assertTemplateUsed(response, 'accounts/wallet.html')

    def test_wallet_context_has_transactions(self):
        response = self.client.get(reverse('wallet'))
        self.assertIn('transactions', response.context)
        self.assertIn('total_earned', response.context)
        self.assertIn('total_spent', response.context)
        self.assertIn('streak_shield_active', response.context)

    def test_wallet_streak_shield_inactive_by_default(self):
        response = self.client.get(reverse('wallet'))
        self.assertFalse(response.context['streak_shield_active'])


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class StreakShieldViewTest(TestCase):

    def setUp(self):
        self.user = make_user(dc_balance=50)
        self.client.login(username=self.user.email, password='testpass123')

    def test_streak_shield_only_post(self):
        response = self.client.get(reverse('streak_shield'))
        self.assertEqual(response.status_code, 405)

    def test_streak_shield_deducts_10_dc(self):
        self.client.post(reverse('streak_shield'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.dc_balance, 40)

    def test_streak_shield_redirects_to_wallet(self):
        response = self.client.post(reverse('streak_shield'))
        self.assertRedirects(response, reverse('wallet'))

    def test_streak_shield_insufficient_balance_shows_error(self):
        self.user.dc_balance = 5
        self.user.save()
        response = self.client.post(reverse('streak_shield'), follow=True)
        messages = list(response.context['messages'])
        self.assertTrue(any('error' in str(m.tags) or 'insuffisant' in str(m).lower() for m in messages))


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class PacksViewTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.client.login(username=self.user.email, password='testpass123')
        self.pack = DCPack.objects.create(
            name='Pack Test', dc_amount=100, price_eur='2.00', is_active=True
        )

    def test_packs_returns_200(self):
        response = self.client.get(reverse('payments:packs'))
        self.assertEqual(response.status_code, 200)

    def test_packs_template_used(self):
        response = self.client.get(reverse('payments:packs'))
        self.assertTemplateUsed(response, 'payments/packs.html')

    def test_packs_context_has_packs(self):
        response = self.client.get(reverse('payments:packs'))
        self.assertIn('packs', response.context)
        self.assertIn(self.pack, response.context['packs'])

    def test_inactive_pack_not_shown(self):
        DCPack.objects.create(name='Inactif', dc_amount=50, price_eur='1.00', is_active=False)
        response = self.client.get(reverse('payments:packs'))
        pack_ids = [p.id for p in response.context['packs']]
        self.assertNotIn(
            DCPack.objects.get(name='Inactif').id,
            pack_ids
        )

    def test_checkout_without_stripe_shows_error(self):
        """Sans Stripe configuré, le checkout doit afficher une erreur et rediriger."""
        response = self.client.post(
            reverse('payments:create_checkout_session', args=[self.pack.id]),
            follow=True,
        )
        messages = list(response.context['messages'])
        self.assertTrue(len(messages) > 0)


@override_settings(SESSION_ENGINE='django.contrib.sessions.backends.db')
class RegisterViewTest(TestCase):

    def test_register_valid_creates_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'Str0ngPass!',
            'password2': 'Str0ngPass!',
        })
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())

    def test_register_duplicate_email_fails(self):
        make_user(email='dup@test.com')
        response = self.client.post(reverse('register'), {
            'username': 'dup2',
            'email': 'dup@test.com',
            'first_name': 'Dup',
            'last_name': 'User',
            'password1': 'Str0ngPass!',
            'password2': 'Str0ngPass!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='dup@test.com').count(), 1)
