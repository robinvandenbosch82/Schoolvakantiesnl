"""Backfill BlogArtikel.gepubliceerd_op uit de Nederlandse weergavestring
(`datum`, bv. '3 november 2023'). Zo heeft de Google News-sitemap een echte
publicatiedatum, ook voor de al geïmporteerde posts."""
from django.db import migrations

NL_MAAND = {
    "januari": 1, "februari": 2, "maart": 3, "april": 4, "mei": 5, "juni": 6,
    "juli": 7, "augustus": 8, "september": 9, "oktober": 10, "november": 11, "december": 12,
}


def backfill(apps, schema_editor):
    from datetime import datetime
    from django.utils import timezone

    BlogArtikel = apps.get_model("core", "BlogArtikel")
    for art in BlogArtikel.objects.filter(gepubliceerd_op__isnull=True):
        delen = (art.datum or "").strip().lower().split()
        if len(delen) != 3 or delen[1] not in NL_MAAND:
            continue
        try:
            dt = datetime(int(delen[2]), NL_MAAND[delen[1]], int(delen[0]), 9, 0)
        except (ValueError, TypeError):
            continue
        art.gepubliceerd_op = timezone.make_aware(dt)
        art.save(update_fields=["gepubliceerd_op"])


class Migration(migrations.Migration):
    dependencies = [("core", "0013_blogartikel_gepubliceerd_op")]
    operations = [migrations.RunPython(backfill, migrations.RunPython.noop)]
