from django.shortcuts import render

def google_oauth_frontend(request):
    return render(request, 'index.html')

# Create your views here.
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.contrib.auth import get_user_model
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from rest_framework_simplejwt.tokens import RefreshToken
from .models import JobListing, JobApplication
from .serializers import UserRegisterSerializer, JobListingSerializer, JobApplicationSerializer, UserSerializer
from .permissions import IsOwnerOrReadOnly, IsRecruiter, IsApplicant
from .auth_utils import send_password_reset_email, token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import AllowAny
User = get_user_model()
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes =[permissions.AllowAny]
    serializer_class = UserRegisterSerializer

# class RegisterView(generics.CreateAPIView):
#     serializer_class = UserRegisterSerializer
#     permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        user_data = UserSerializer(user, context={'request': request}).data
        response_data = {
            'user': user_data,
            'access': access_token,
            'refresh': refresh_token,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
 

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def google_oauth_view(request):
    token = request.data.get('id_token')
    print(" RECEIVED DATA:", request.data)
    if not token:
        return Response({'detail':'id_token required'}, status=400)
    try:
        idinfo = id_token.verify_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
    except Exception as e:
        return Response({'detail':'Invalid token', 'error': str(e)}, status=400)

    google_id = idinfo['sub']
    email = idinfo['email']
    username = idinfo.get('name', email.split('@')[0])

    user, created = User.objects.get_or_create(
        google_id=google_id,
        defaults={'username': username, 'email': email, 'role': User.ROLE_APPLICANT}
    )
    if not created:
        user.email = email
        user.save()

    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token), 
        'refresh': str(refresh), 
        'user': {'id':user.id,'email':user.email,'username':user.username,'role':user.role}
    })                
    
class JobListingViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.select_related('posted_by').all()
    serializer_class = JobListingSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsRecruiter()]
        if self.action in ['update','partial_update','destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsApplicant()]
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        return JobApplication.objects.filter(applicant=self.request.user).select_related('job_listing')

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    email = request.data.get('email')
    if not email:
        return Response({'detail':'email required'}, status=400)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail':'If account exists, password reset email will be sent.'})
    send_password_reset_email(user)
    return Response({'detail':'Password reset email sent if account exists.'})

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def confirm_password_reset(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        return Response({'detail':'Invalid user'}, status=400)
    if not token_generator.check_token(user, token):
        return Response({'detail':'Invalid or expired token'}, status=400)
    password = request.data.get('password')
    if not password:
        return Response({'detail':'password required'}, status=400)
    user.set_password(password)
    user.save()
    return Response({'detail':'Password has been reset.'})

class TokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # data['user'] = {
        #     'id': self.user.id,
        #     'username': self.user.username,
        #     'email': self.user.email,
        #     'role': self.user.role,
        # }
        data['user'] = UserSerializer(self.user).data
        return data

class TokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer



