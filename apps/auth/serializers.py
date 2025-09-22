from rest_framework import serializers


class OAuthTokenSerializer(serializers.Serializer):
    client_id = serializers.CharField()
    client_secret = serializers.CharField()
    grant_type = serializers.ChoiceField(choices=["client_credentials"], default="client_credentials")

