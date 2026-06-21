from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from accounts.models import DCTransaction, Referral, PromoCode
from accounts.services import DCService
from payments.models import DCPack, DCPackOrder, RechargeCode
from payments.services import ManualPaymentService, RechargeCodeService
from learning.models import Course, TD, ContentPurchase
from exams.models import Exam, ExamSession
from .serializers import (
    UserSerializer, UserRegisterSerializer, UserLoginSerializer,
    DCTransactionSerializer, WalletSerializer,
    DCPackSerializer, DCPackOrderSerializer, RechargeCodeSerializer,
    CourseSerializer, TDSerializer, ExamSerializer, ExamSessionSerializer,
    PromoCodeSerializer, ReferralSerializer
)

User = get_user_model()


class AuthViewSet(viewsets.ViewSet):
    """ViewSet pour l'authentification."""
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        """Inscription d'un nouvel utilisateur."""
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Connexion d'un utilisateur."""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'user': UserSerializer(user).data,
                    'token': token.key
                }, status=status.HTTP_200_OK)
            return Response(
                {'error': 'Email ou mot de passe incorrect'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Déconnexion de l'utilisateur."""
        if request.user.is_authenticated:
            try:
                request.user.auth_token.delete()
            except:
                pass
            logout(request)
            return Response({'message': 'Déconnexion réussie'}, status=status.HTTP_200_OK)
        return Response({'error': 'Non authentifié'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtenir les informations de l'utilisateur connecté."""
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        return Response({'error': 'Non authentifié'}, status=status.HTTP_401_UNAUTHORIZED)


class WalletViewSet(viewsets.ViewSet):
    """ViewSet pour le portefeuille DC."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Obtenir le solde et les transactions DC de l'utilisateur."""
        transactions = DCTransaction.objects.filter(user=request.user).order_by('-created_at')[:20]
        serializer = WalletSerializer({
            'dc_balance': request.user.dc_balance,
            'transactions': transactions
        })
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def apply_code(self, request):
        """Appliquer un code de recharge."""
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        success, message, dc_amount = RechargeCodeService.redeem_code(request.user, code)
        if success:
            return Response({
                'message': message,
                'dc_amount': dc_amount,
                'new_balance': request.user.dc_balance
            }, status=status.HTTP_200_OK)
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)


class DCPackViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les packs DC."""
    queryset = DCPack.objects.filter(is_active=True).order_by('order')
    serializer_class = DCPackSerializer
    permission_classes = [permissions.AllowAny]


class DCPackOrderViewSet(viewsets.ModelViewSet):
    """ViewSet pour les commandes de packs DC."""
    serializer_class = DCPackOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DCPackOrder.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request):
        """Créer une commande de paiement manuel."""
        pack_id = request.data.get('pack_id')
        payment_method = request.data.get('payment_method')
        transaction_reference = request.data.get('transaction_reference', '')
        
        if not pack_id or not payment_method:
            return Response(
                {'error': 'pack_id et payment_method requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pack = DCPack.objects.get(id=pack_id, is_active=True)
        except DCPack.DoesNotExist:
            return Response({'error': 'Pack introuvable'}, status=status.HTTP_404_NOT_FOUND)
        
        order = ManualPaymentService.create_manual_order(
            user=request.user,
            pack=pack,
            payment_method=payment_method,
            transaction_reference=transaction_reference
        )
        
        return Response(DCPackOrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les cours."""
    queryset = Course.objects.all().order_by('-created_at')
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class TDViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les TD."""
    queryset = TD.objects.all().order_by('-created_at')
    serializer_class = TDSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les examens."""
    queryset = Exam.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExamSessionViewSet(viewsets.ModelViewSet):
    """ViewSet pour les sessions d'examen."""
    serializer_class = ExamSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExamSession.objects.filter(user=self.request.user).order_by('-started_at')


class PromoCodeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les codes promo."""
    queryset = PromoCode.objects.filter(is_active=True)
    serializer_class = PromoCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Valider un code promo."""
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            promo_code = PromoCode.objects.get(code=code)
        except PromoCode.DoesNotExist:
            return Response({'error': 'Code introuvable'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PromoCodeSerializer(promo_code)
        return Response(serializer.data)


class ReferralViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour le parrainage."""
    serializer_class = ReferralSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Referral.objects.filter(referrer=self.request.user)

    @action(detail=False, methods=['get'])
    def my_code(self, request):
        """Obtenir le code de parrainage de l'utilisateur."""
        try:
            referral = Referral.objects.get(referrer=request.user)
            return Response({'referral_code': referral.referral_code})
        except Referral.DoesNotExist:
            return Response({'error': 'Code de parrainage introuvable'}, status=status.HTTP_404_NOT_FOUND)

