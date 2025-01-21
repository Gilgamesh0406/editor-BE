from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from django.shortcuts import get_object_or_404


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "User registered successfully.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Deserialize the input data
            serializer = LoginSerializer(data=request.data)
            
            # Validate the input data
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                
                # Get the user by email
                item = User.objects.filter(email=email).first()
                if item is None:
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
                user = authenticate(request, username=item, password=password)
                print("response: ", user)
                user_data = UserSerializer(user).data
                if user is not None:
                        # Login the user and create a JWT token
                        login(request, user)
                        refresh = RefreshToken.for_user(user)
                        
                        return Response({
                            "message": "Login successful.",
                            "token": str(refresh.access_token),
                            "session": str(refresh),
                            "user": user_data,
                        }, status=status.HTTP_200_OK)
                
                # Return an error response if user does not exist or password is incorrect
                return Response({"message": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
            # Return errors from serializer if data is invalid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Log the error for debugging
            print(f"An error occurred: {e}")
            
            # Return a generic error response
            return Response({"message": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleLoginView(APIView):
    def get(self, request, *args, **kwargs):
        # This view is used to initiate the OAuth login process with Google
        return Response({"message": "Google OAuth login initiated."})


class GithubLoginView(APIView):
    def get(self, request, *args, **kwargs):
        # This view is used to initiate the OAuth login process with GitHub
        return Response({"message": "GitHub OAuth login initiated."})
