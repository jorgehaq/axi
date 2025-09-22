from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = "apps.auth"
    label = "axi_auth"  # evitar conflicto con django.contrib.auth
    verbose_name = "Autenticación"
