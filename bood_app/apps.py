from django.apps import AppConfig


class BoodAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bood_app"
    verbose_name = "КБЖУ"

    def ready(self) -> None:
        import bood_app.signals
