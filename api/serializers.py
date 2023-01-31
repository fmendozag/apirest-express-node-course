from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # The default result (access/refresh tokens)
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        # Custom data you want to include
        data.update({'usuario': {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'nombre': '{} {}'.format(self.user.first_name, self.user.last_name)
        }})
        # and everything else you want to send in the response
        return data
