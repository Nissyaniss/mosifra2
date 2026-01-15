# pour la recherche de pays avec pycountry
# il contient la base de données ISO de tous les pays du monde
import gettext
import pycountry

# traduction française intégrée à pycountry
french = gettext.translation('iso3166-1', pycountry.LOCALES_DIR, languages=['fr'])

# pays avec des abréviations connues
EXTRA_ALIASES = {
    "US": ["usa", "amérique"],
    "GB": ["uk", "angleterre"],
    "AE": ["dubai", "émirats"],
}


def get_country_search_names(code):
    code = code.upper()
    names = [code.lower()]
    
    country = pycountry.countries.get(alpha_2=code)
    if country:
        # nom en anglais
        names.append(country.name.lower())
        # nom en français (traduction automatique)
        french_name = french.gettext(country.name)
        if french_name != country.name:
            names.append(french_name.lower())
        # nom courant si différent
        if hasattr(country, "common_name"):
            names.append(country.common_name.lower())
            french_common = french.gettext(country.common_name)
            if french_common != country.common_name:
                names.append(french_common.lower())
        if hasattr(country, "official_name"):
            names.append(country.official_name.lower())
    
    if code in EXTRA_ALIASES:
        names.extend(EXTRA_ALIASES[code])
    
    return names


def get_all_country_codes():
    """Retourne l'ensemble de tous les codes ISO alpha-2 valides (250+ pays)."""
    return {country.alpha_2 for country in pycountry.countries}


def get_country_choices():
    """
    Retourne une liste de tuples (code, nom en français) pour les formulaires.
    """
    choices = []
    for country in pycountry.countries:
        name = getattr(country, "common_name", None) or country.name
        # traduit en français
        french_name = french.gettext(name)
        choices.append((country.alpha_2, french_name))
    
    choices.sort(key=lambda x: x[1])
    return choices
