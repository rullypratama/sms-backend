from datetime import datetime

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import jwt_response_payload_handler
from django.http import JsonResponse, HttpRequest, HttpResponse
from rest_framework.permissions import IsAuthenticated

from users.models import User


class ObtainJSONWebToken(APIView):
    """
    API View that receives a POST with a user's username and password.

    Returns a JSON Web Token that can be used for authenticated requests.

    Override from default DRF JWT auth package
    """
    serializer_class = JSONWebTokenSerializer
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'view': self,
        }

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.
        You may want to override this if you need to provide different
        serializations depending on the incoming request.
        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__)
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        request_data = request.data
        if 'email' in request_data:
            request_data['email'] = request_data.get('email').lower()
        elif 'phone' in request_data:
            user_by_phone = User.objects.filter(phone_number=request_data.get('phone')).first()
            request_data['email'] = user_by_phone.email.lower()
        serializer = self.get_serializer(data=request_data, context={'request': request})

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user

            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)

            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    response.data['token'],
                                    expires=expiration,
                                    httponly=True)
            return response

        return Response({'message': 'Invalid Password'}, status=status.HTTP_400_BAD_REQUEST)


obtain_jwt_token = ObtainJSONWebToken.as_view()


class UserDetailApi(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """ Get user detail based on request user.id
        """
        user = User.objects.get(pk=request.user.pk)

        resp_json = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'email': user.email,
            'health_facility_name': user.health_facility.name,
            'address': user.health_facility.address
        }
        return JsonResponse(resp_json, safe=False)


