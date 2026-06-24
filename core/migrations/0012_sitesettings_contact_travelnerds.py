"""Zet de contactgegevens op de bestaande site-instellingen-singleton:
telefoon 085 060 0043 (zichtbaar) + e-mail partner@travelnerds.nl. Overschrijft
alleen de oude default/lege waarden, zodat handmatige admin-aanpassingen blijven."""
from django.db import migrations

OUD_EMAILS = {"", "hallo@schoolvakanties.nl"}


def contact_travelnerds(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    s = SiteSettings.objects.filter(pk=1).first()
    if not s:
        return
    changed = []
    if (s.email or "") in OUD_EMAILS:
        s.email = "partner@travelnerds.nl"; changed.append("email")
    if not (s.phone or "").strip():
        s.phone = "085 060 0043"; changed.append("phone")
    if not s.show_phone:
        s.show_phone = True; changed.append("show_phone")
    if changed:
        s.save(update_fields=changed)


class Migration(migrations.Migration):
    dependencies = [("core", "0011_alter_sitesettings_email_alter_sitesettings_phone_and_more")]
    operations = [migrations.RunPython(contact_travelnerds, migrations.RunPython.noop)]
