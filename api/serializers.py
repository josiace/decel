from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.models import DCTransaction, Referral, PromoCode
from payments.models import DCPack, DCPackOrder, RechargeCode
from learning.models import Course, TD, ContentPurchase
from exams.models import Exam, ExamSession

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle User."""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'dc_balance', 'total_xp', 'level', 'created_at']
        read_only_fields = ['id', 'dc_balance', 'total_xp', 'level', 'created_at']


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription d'un utilisateur."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm', 'phone_number', 'country']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer pour la connexion d'un utilisateur."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})


class DCTransactionSerializer(serializers.ModelSerializer):
    """Serializer pour les transactions DC."""
    class Meta:
        model = DCTransaction
        fields = ['id', 'transaction_type', 'amount', 'balance_after', 'description', 'created_at']
        read_only_fields = ['id', 'balance_after', 'created_at']


class WalletSerializer(serializers.Serializer):
    """Serializer pour le portefeuille DC."""
    dc_balance = serializers.IntegerField(read_only=True)
    transactions = DCTransactionSerializer(many=True, read_only=True)


class DCPackSerializer(serializers.ModelSerializer):
    """Serializer pour les packs DC."""
    dc_per_cfa = serializers.SerializerMethodField()

    class Meta:
        model = DCPack
        fields = ['id', 'name', 'dc_amount', 'price_cfa', 'dc_per_cfa', 'is_popular', 'is_active', 'order']
        read_only_fields = ['id']

    def get_dc_per_cfa(self, obj):
        return obj.dc_per_cfa


class DCPackOrderSerializer(serializers.ModelSerializer):
    """Serializer pour les commandes de packs DC."""
    pack = DCPackSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = DCPackOrder
        fields = ['id', 'user', 'pack', 'dc_amount', 'price_paid_cfa', 'payment_method', 'status', 'created_at', 'completed_at']
        read_only_fields = ['id', 'user', 'created_at', 'completed_at']


class RechargeCodeSerializer(serializers.ModelSerializer):
    """Serializer pour les codes de recharge."""
    class Meta:
        model = RechargeCode
        fields = ['code', 'dc_amount', 'status', 'expires_at']
        read_only_fields = ['code', 'status']


class CourseSerializer(serializers.ModelSerializer):
    """Serializer pour les cours."""
    author_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    is_purchased = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'author', 'author_name', 'subject', 'subject_name', 'content_type', 'dc_price', 'is_purchased', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name() if obj.author else None

    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else None

    def get_is_purchased(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ContentPurchase.objects.filter(
                user=request.user,
                content_type='course',
                course_id=obj.id
            ).exists()
        return False


class TDSerializer(serializers.ModelSerializer):
    """Serializer pour les TD."""
    author_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    is_purchased = serializers.SerializerMethodField()

    class Meta:
        model = TD
        fields = ['id', 'title', 'description', 'author', 'author_name', 'subject', 'subject_name', 'content_type', 'dc_price', 'is_purchased', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_author_name(self, obj):
        return obj.author.get_full_name() if obj.author else None

    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else None

    def get_is_purchased(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ContentPurchase.objects.filter(
                user=request.user,
                content_type='td',
                td_id=obj.id
            ).exists()
        return False


class ExamSerializer(serializers.ModelSerializer):
    """Serializer pour les examens."""
    subject_name = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = ['id', 'title', 'description', 'subject', 'subject_name', 'duration_minutes', 'passing_score', 'question_count', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else None

    def get_question_count(self, obj):
        return obj.questions.count()


class ExamSessionSerializer(serializers.ModelSerializer):
    """Serializer pour les sessions d'examen."""
    exam = ExamSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = ExamSession
        fields = ['id', 'exam', 'user', 'score', 'total_questions', 'passed', 'started_at', 'completed_at']
        read_only_fields = ['id', 'user', 'started_at', 'completed_at']


class PromoCodeSerializer(serializers.ModelSerializer):
    """Serializer pour les codes promo."""
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = PromoCode
        fields = ['code', 'code_type', 'value', 'is_valid', 'valid_from', 'valid_until']
        read_only_fields = ['code']

    def get_is_valid(self, obj):
        return obj.is_valid()


class ReferralSerializer(serializers.ModelSerializer):
    """Serializer pour le parrainage."""
    referrer_email = serializers.SerializerMethodField()
    referred_email = serializers.SerializerMethodField()

    class Meta:
        model = Referral
        fields = ['id', 'referral_code', 'referrer_email', 'referred_email', 'reward_dc', 'referred_reward_dc', 'is_completed', 'created_at']
        read_only_fields = ['id', 'referral_code', 'created_at']

    def get_referrer_email(self, obj):
        return obj.referrer.email if obj.referrer else None

    def get_referred_email(self, obj):
        return obj.referred.email if obj.referred else None
