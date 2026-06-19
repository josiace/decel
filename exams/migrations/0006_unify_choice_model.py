# Generated migration to unify Choice model and remove QuestionOption

from django.db import migrations, models
import django.db.models.deletion


def migrate_question_options_to_choices(apps, schema_editor):
    """Migrate QuestionOption data to Choice model."""
    QuestionOption = apps.get_model('exams', 'QuestionOption')
    Choice = apps.get_model('exams', 'Choice')
    
    for option in QuestionOption.objects.all():
        # Check if a choice with same label/text already exists for this question
        existing = Choice.objects.filter(
            question=option.question,
            text=option.text
        ).first()
        
        if not existing:
            # Create new Choice from QuestionOption
            Choice.objects.create(
                question=option.question,
                label=option.label,
                text=option.text,
                is_correct=option.is_correct,
                order=option.order
            )


def reverse_migrate_question_options_to_choices(apps, schema_editor):
    """Reverse migration - no-op since we're deleting QuestionOption."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0005_alter_questionoption_unique_together'),
    ]

    operations = [
        # Remove selected_options field from UserAnswer
        migrations.RemoveField(
            model_name='useranswer',
            name='selected_options',
        ),
        
        # Add label field to Choice (nullable initially)
        migrations.AddField(
            model_name='choice',
            name='label',
            field=models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')], max_length=10, null=True, verbose_name='Label'),
        ),
        
        # Migrate data from QuestionOption to Choice
        migrations.RunPython(
            migrate_question_options_to_choices,
            reverse_migrate_question_options_to_choices
        ),
        
        # Delete QuestionOption model
        migrations.DeleteModel(
            name='QuestionOption',
        ),
        
        # Update Choice help text
        migrations.AlterField(
            model_name='choice',
            name='label',
            field=models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')], help_text='Label optionnel (A, B, C, D, etc.) - utile pour les questions sur fichier', max_length=10, null=True, verbose_name='Label'),
        ),
    ]
