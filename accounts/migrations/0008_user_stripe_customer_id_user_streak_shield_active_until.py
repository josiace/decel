from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_dctransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='stripe_customer_id',
            field=models.CharField(
                blank=True,
                help_text='ID client Stripe pour les paiements',
                max_length=255,
                verbose_name='ID client Stripe'
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='streak_shield_active_until',
            field=models.DateField(
                blank=True,
                null=True,
                help_text="Date jusqu'à laquelle le streak est protégé",
                verbose_name="Streak Shield actif jusqu'au"
            ),
        ),
    ]
