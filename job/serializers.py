from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import JobListing, JobApplication

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email','role','google_id')

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ('id','username','email','password','role','google_id')

    # def validate_password(self, value):
    #     validate_password(value)
    #     return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class JobListingSerializer(serializers.ModelSerializer):
    posted_by = serializers.ReadOnlyField(source='posted_by.id')
    posted_by_username = serializers.ReadOnlyField(source='posted_by.username')

    class Meta:
        model = JobListing
        fields = ('id','title','description','company','location','posted_by','posted_by_username','created_at','updated_at')
        read_only_fields = ('id','posted_by','posted_by_username','created_at','updated_at')

class JobApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.ReadOnlyField(source='applicant.id')
    job_listing_detail = JobListingSerializer(source='job_listing', read_only=True)

    class Meta:
        model = JobApplication
        fields = ('id','job_listing','job_listing_detail','applicant','resume_link','cover_letter','status','applied_at','updated_at')
        read_only_fields = ('id','applicant','status','applied_at','updated_at','job_listing_detail')

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request,'user',None)
        job = attrs.get('job_listing')
        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")
        if job.posted_by_id == user.id:
            raise serializers.ValidationError("Cannot apply to your own job.")
        from .models import JobApplication as JA
        if JA.objects.filter(job_listing=job, applicant=user).exists():
            raise serializers.ValidationError("Already applied to this job.")
        if getattr(user,'role',None) != User.ROLE_APPLICANT:
            raise serializers.ValidationError("Only applicants can create applications.")
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['applicant'] = request.user
        return super().create(validated_data)
