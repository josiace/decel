from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_user_stripe_customer_id_user_streak_shield_active_until'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor',
            name='plan',
            field=models.CharField(
                choices=[('free', 'Créateur Gratuit'), ('pro', 'Créateur Pro'), ('academy', 'Académie')],
                default='free',
                max_length=20,
                verbose_name='Plan'
            ),
        ),
        migrations.AddField(
            model_name='contributor',
            name='plan_expires_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Expiration du plan'),
        ),
        migrations.AddField(
            model_name='contributor',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, max_length=255, verbose_name='ID abonnement Stripe'),
        ),
        migrations.AddField(
            model_name='contributor',
            name='total_content_sales',
            field=models.IntegerField(default=0, verbose_name='Total ventes contenu'),
        ),
        migrations.AddField(
            model_name='contributor',
            name='total_dc_earned',
            field=models.IntegerField(default=0, verbose_name='Total DC gagnés'),
        ),
    ]
