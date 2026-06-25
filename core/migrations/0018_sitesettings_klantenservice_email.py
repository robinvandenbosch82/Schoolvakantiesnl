"""Werk het contact-e-mailadres op de site-instellingen-singleton bij:
partner@travelnerds.nl -> klantenservice@travelnerds.nl. Overschrijft alleen de
bekende oude waarden, zodat een handmatige admin-aanpassing intact blijft."""
from django.db import migrations

OUD_EMAILS = {"partner@travelnerds.nl", "", "hallo@schoolvakanties.nl"}
NIEUW_EMAIL = "klantenservice@travelnerds.nl"


def naar_klantenservice(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    s = SiteSettings.objects.filter(pk=1).first()
    if s and (s.email or "") in OUD_EMAILS:
        s.email = NIEUW_EMAIL
        s.save(update_fields=["email"])


def terug(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    s = SiteSettings.objects.filter(pk=1).first()
    if s and s.email == NIEUW_EMAIL:
        s.email = "partner@travelnerds.nl"
        s.save(update_fields=["email"])


class Migration(migrations.Migration):
    dependencies = [("core", "0017_widget_widgetpagina")]
    operations = [migrations.RunPython(naar_klantenservice, terug)]
