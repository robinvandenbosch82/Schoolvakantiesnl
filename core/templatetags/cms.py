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
from django.utils.html import escape

register = template.Library()


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
