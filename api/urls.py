from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet, WalletViewSet, DCPackViewSet, DCPackOrderViewSet,
    CourseViewSet, TDViewSet, ExamViewSet, ExamSessionViewSet,
    PromoCodeViewSet, ReferralViewSet
)

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'wallet', WalletViewSet, basename='wallet')
router.register(r'packs', DCPackViewSet, basename='packs')
router.register(r'orders', DCPackOrderViewSet, basename='orders')
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'tds', TDViewSet, basename='tds')
router.register(r'exams', ExamViewSet, basename='exams')
router.register(r'exam-sessions', ExamSessionViewSet, basename='exam-sessions')
router.register(r'promo-codes', PromoCodeViewSet, basename='promo-codes')
router.register(r'referrals', ReferralViewSet, basename='referrals')

urlpatterns = [
    path('', include(router.urls)),
]
