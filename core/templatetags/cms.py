"""
Admin-bewerkbare paginacopy via het SectieTekst-model.

Gebruik in een template:

    {% load cms %}
    <h2>{% stekst "over_ons" "missie_kop" %}Standaardkop als er niets in de admin staat{% endstekst %}</h2>

`{% stekst pagina sleutel %}…{% endstekst %}` toont de tekst die de redactie in de
admin heeft gezet (SectieTekst met die pagina+sleutel), en anders de
standaardinhoud tussen de tags. Zo is de copy bewerkbaar in de admin én breekt de
pagina nooit als er nog geen rij is. Geen cache: een wijziging in de admin is
direct zichtbaar.
"""
from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

# Core-CSS die op elke pagina nodig is. Inline zetten haalt 5 render-blocking
# netwerkverzoeken weg (belangrijk op een trage origin): de tekst kan schilderen
# zodra de HTML binnen is, zonder op losse CSS-bestanden te wachten. Volgorde =
# cascade-volgorde. Pagina-specifieke CSS blijft in {% block extra_css %}.
_CORE_CSS = ["css/tokens.css", "css/styles.css", "css/components.css",
             "css/header.css", "css/blog.css"]
_inline_css_cache = None


@register.simple_tag
def inline_core_css():
    """Geef de samengevoegde core-CSS terug als één <style>-blok."""
    global _inline_css_cache
    if _inline_css_cache is not None and not settings.DEBUG:
        return _inline_css_cache
    parts = []
    for rel in _CORE_CSS:
        path = finders.find(rel)
        if not path:
            continue
        with open(path, encoding="utf-8") as fh:
            parts.append(f"/* {rel} */\n{fh.read()}")
    html = mark_safe("<style>\n" + "\n".join(parts) + "\n</style>")
    if not settings.DEBUG:
        _inline_css_cache = html
    return html


@register.tag("stekst")
def do_stekst(parser, token):
    bits = token.split_contents()
    if len(bits) != 3:
        raise template.TemplateSyntaxError(
            '{% stekst "pagina" "sleutel" %}standaard{% endstekst %}')
    pagina = bits[1].strip("\"'")
    sleutel = bits[2].strip("\"'")
    nodelist = parser.parse(("endstekst",))
    parser.delete_first_token()
    return _StekstNode(pagina, sleutel, nodelist)


class _StekstNode(template.Node):
    def __init__(self, pagina, sleutel, nodelist):
        self.pagina = pagina
        self.sleutel = sleutel
        self.nodelist = nodelist

    def render(self, context):
        from core.models import SectieTekst
        val = (SectieTekst.objects
               .filter(pagina=self.pagina, sleutel=self.sleutel)
               .values_list("tekst", flat=True).first())
        if val and val.strip():
            return escape(val)
        return self.nodelist.render(context)
