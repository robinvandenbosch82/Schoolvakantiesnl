"""Rename het GB-land naar 'Engeland' met slug 'engeland', zodat de geïndexeerde
live-URL /engeland/ (verreweg het meeste VK-verkeer) op zijn eigen URL blijft.
Schotland/Wales/Noord-Ierland redirecten in de view 301 naar /engeland/."""
from django.db import migrations


def gb_naar_engeland(apps, schema_editor):
    Land = apps.get_model("core", "Land")
    gb = Land.objects.filter(iso_code="GB").first()
    if gb:
        gb.naam = "Engeland"
        gb.slug = "engeland"
        gb.save(update_fields=["naam", "slug"])


def terug(apps, schema_editor):
    Land = apps.get_model("core", "Land")
    gb = Land.objects.filter(iso_code="GB").first()
    if gb:
        gb.naam = "Verenigd Koninkrijk"
        gb.slug = "verenigd-koninkrijk"
        gb.save(update_fields=["naam", "slug"])


class Migration(migrations.Migration):
    dependencies = [("core", "0009_page_body_html_sitesettings_bedrijfsnaam_and_more")]
    operations = [migrations.RunPython(gb_naar_engeland, terug)]
