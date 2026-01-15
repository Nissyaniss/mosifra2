import csv
import io
import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import RegexValidator, validate_email

from .countries import get_country_search_names, get_all_country_codes

User = get_user_model()

# ensemble des codes pays valides (utilisé pour validation)
ISO_ALPHA2 = get_all_country_codes()




def _is_strong_password(value: str) -> bool:
    if len(value) < 8:
        return False
    if not re.search(r"[A-Z]", value):
        return False
    if not re.search(r"[a-z]", value):
        return False
    if not re.search(r"[^\w]", value):
        return False
    return True


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=User.Role.choices, label="Type de compte")
    organisation_name = forms.CharField(label="Nom de l'organisation", required=False)
    country_code = forms.CharField(
        label="Pays (code ISO 2 lettres)",
        required=False,
        max_length=2,
        validators=[RegexValidator(r"^[A-Za-z]{2}$", "Code pays sur 2 lettres (ex : FR).")],
    )
    organisation_location = forms.CharField(label="Lieu", required=False, max_length=255)
    organisation_phone = forms.CharField(label="Téléphone", required=False, max_length=64)
    organisation_site = forms.URLField(label="Site web", required=False)
    organisation_description = forms.CharField(
        label="Description", required=False, widget=forms.Textarea
    )
    organisation_logo = forms.ImageField(label="Logo", required=False)
    #checkbox pour accepter les cgv, obligatoire
    terms = forms.BooleanField(
        label="J'accepte les termes d'utilisation et la politique de confidentialité",
        required=True,
        error_messages={"required": "Tu dois accepter les conditions d'utilisation pour continuer."}
    )

    class Meta:
        model = User
        fields = ("username", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_input = "w-full rounded-full border border-slate-400 px-5 py-3 text-sm md:text-base text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-primary bg-transparent placeholder-slate-500"
        role_value = None
        if self.data and self.data.get("role"):
            role_value = self.data.get("role")
        elif self.initial.get("role"):
            role_value = self.initial.get("role")
        organisation_placeholder = "Nom de l'entreprise"
        if role_value == User.Role.INSTITUTION:
            organisation_placeholder = "Nom de l'établissement"
        placeholders = {
            "organisation_name": organisation_placeholder,
            "email": "Email",
            "country_code": "Code pays (ex : FR)",
            "password1": "Mot de passe",
            "password2": "Confirmer le mot de passe",
            "organisation_location": "Lieu",
            "organisation_phone": "Téléphone",
            "organisation_site": "https://...",
        }
        for name in (
            "organisation_name",
            "email",
            "country_code",
            "password1",
            "password2",
            "organisation_location",
            "organisation_phone",
            "organisation_site",
        ):
            field = self.fields[name]
            field.widget.attrs.update(
                {
                    "class": base_input,
                    "placeholder": placeholders.get(name, field.label),
                }
            )
        self.fields["organisation_name"].label = organisation_placeholder
        self.fields["organisation_description"].widget.attrs.update(
            {
                "class": "w-full px-5 py-3 text-sm md:text-base text-slate-900 focus:outline-none bg-transparent resize-none",
                "style": "border:none;outline:none;box-shadow:none;",
                "placeholder": "Présente votre structure...",
                "rows": 4,
            }
        )
        self.fields["organisation_logo"].widget.attrs.update({"class": "hidden"})
        self.fields["username"].widget = forms.HiddenInput()
        self.fields["username"].required = False

        role_value = self.initial.get("role") or self.data.get("role")
        if role_value:
            self.fields["role"].initial = role_value
            self.fields["role"].widget = forms.HiddenInput()
        else:
            self.fields["role"].widget.attrs.update({"class": base_input})

    def clean_email(self):
        email = self.cleaned_data.get("email")
        #on vérifie si l'email est déjà pris pour éviter les doublons
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean(self):
        cleaned = super().clean()
        pwd1 = cleaned.get("password1")
        pwd2 = cleaned.get("password2")
        if pwd1 and pwd2 and pwd1 != pwd2:
            self.add_error("password2", "Les mots de passe ne correspondent pas.")
        if pwd1 and not _is_strong_password(pwd1):
            self.add_error("password1", "Au moins 8 caractères, une majuscule, une minuscule et un caractère spécial.")

        role = cleaned.get("role")
        organisation = (cleaned.get("organisation_name") or "").strip()
        country_code = (cleaned.get("country_code") or "").strip().upper()

        if role in {User.Role.COMPANY, User.Role.INSTITUTION}:
            if not organisation:
                self.add_error("organisation_name", "Renseigne le nom de l'organisation.")
            if country_code and country_code.upper() not in ISO_ALPHA2:
                self.add_error("country_code", "Code pays invalide (ex : FR, CA, US).")
        else:
            cleaned["organisation_name"] = ""
            if not country_code:
                country_code = ""

        cleaned["country_code"] = country_code
        return cleaned

    def clean_organisation_description(self):
        desc = self.cleaned_data.get("organisation_description", "")
        if len(desc) > 10000:
            raise forms.ValidationError("La description ne doit pas dépasser 10000 caractères.")
        import bleach
        allowed = ['b', 'i', 'u', 'strong', 'em', 'p', 'br', 'ul', 'li']
        return bleach.clean(desc, tags=allowed, strip=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data["password1"])
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")
    error_messages = {
        "invalid_login": "Email ou mot de passe incorrect.",
        "inactive": "Ce compte est désactivé.",
    }

    def clean(self):
        email = self.cleaned_data.get("username")
        if email:
            try:
                user = User.objects.get(email__iexact=email)
                self.cleaned_data["username"] = user.get_username()
            except User.DoesNotExist:
                pass
        return super().clean()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_attrs = {
            "class": "w-full rounded-xl border border-slate-300 bg-transparent px-4 py-3 text-base text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary",
            "style": "background-color: transparent;",
        }
        self.fields["username"].widget.attrs.update(
            {**base_attrs, "placeholder": "Email"}
        )
        self.fields["password"].widget.attrs.update(
            {**base_attrs, "placeholder": "Mot de passe"}
        )


class TwoFactorForm(forms.Form):
    code = forms.CharField(
        label="Code",
        max_length=6,
        min_length=6,
        #regex pour forcer 6 chiffres exactement
        validators=[RegexValidator(r"^\d{6}$", message="Le code doit contenir uniquement 6 chiffres.")],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["code"].widget.attrs.update(
            {
                "class": "peer w-[260px] rounded-full border border-slate-400 bg-white px-6 py-4 text-center text-2xl tracking-[0.5em] text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary",
                "placeholder": "_ _ _ _ _ _",
                "inputmode": "numeric",
                "maxlength": "6",
                "autocomplete": "one-time-code",
                "pattern": r"\d*",
                "style": "border-radius:999px;",
                "oninput": "this.value=this.value.replace(/[^0-9]/g,'').slice(0,6)",
            }
        )


class InvitationUploadForm(forms.Form):
    csv_file = forms.FileField(label="Fichier CSV (UTF-8)")

    MAX_ROWS = 500

    def clean_csv_file(self):
        uploaded = self.cleaned_data["csv_file"]
        #on limite la taille pour pas faire planter le serveur
        if uploaded.size > 1_000_000:
            raise forms.ValidationError("Fichier trop volumineux (max 1 Mo).")
        if not uploaded.name.lower().endswith(".csv"):
            raise forms.ValidationError("Le fichier doit être au format .csv")
        return uploaded

    def read_rows(self):
        file = self.cleaned_data["csv_file"]
        raw = file.read()
        text = None
        for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1", "cp437"):
            try:
                text = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        if text is None:
            raise forms.ValidationError("Encodage non supporté. Exportez le CSV en UTF-8.")
        
        first_line = text.split("\n")[0] if text else ""
        delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
        
        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
        fieldnames = [f.strip().lower() for f in (reader.fieldnames or [])]
        reader.fieldnames = fieldnames
        
        required = {
            "email",
            "prenom",
            "nom",
            "filiere_ou_parcours",
            "niveau",
            "annee_academique",
        }
        missing = required - set(fieldnames)
        if missing:
            raise forms.ValidationError(f"Colonnes manquantes : {', '.join(sorted(missing))}")
        rows = list(reader)
        if not rows:
            raise forms.ValidationError("Le fichier est vide.")
        if len(rows) > self.MAX_ROWS:
            raise forms.ValidationError(f"Limité à {self.MAX_ROWS} lignes par import.")
        return rows


class InvitationAcceptForm(forms.Form):
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        pwd1 = cleaned.get("password1")
        pwd2 = cleaned.get("password2")
        if pwd1 and pwd2 and pwd1 != pwd2:
            self.add_error("password2", "Les mots de passe ne correspondent pas.")
        if pwd1 and not _is_strong_password(pwd1):
            self.add_error("password1", "Mot de passe trop faible.")
        return cleaned


from .models import Offer
import bleach

ALLOWED_TAGS = ['b', 'i', 'u', 'strong', 'em', 'p', 'br', 'ul', 'li']


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["title", "salary", "contract_type", "location", "skills", "phone", "remote", "start_date", "duration", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_input = "w-full rounded-full border border-slate-400 px-5 py-3 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-primary bg-white"
        select_style = "w-full rounded-full border border-slate-400 px-5 py-3 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-primary bg-white appearance-none cursor-pointer"
        for name, field in self.fields.items():
            if name == "remote":
                continue
            if name == "description":
                field.widget.attrs.update({"class": "w-full rounded-2xl border border-slate-400 px-5 py-3 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-primary bg-white", "rows": 6})
            elif name == "contract_type":
                field.widget.attrs.update({"class": select_style})
            else:
                field.widget.attrs.update({"class": base_input})
        self.fields["duration"].required = True

    def clean_description(self):
        desc = self.cleaned_data.get("description", "")
        if len(desc) > 10000:
            raise forms.ValidationError("La description ne doit pas dépasser 10000 caractères.")
        return bleach.clean(desc, tags=ALLOWED_TAGS, strip=True)

    def clean_location(self):
        loc = self.cleaned_data.get("location", "")
        if len(loc) > 255:
            raise forms.ValidationError("Le lieu ne doit pas dépasser 255 caractères.")
        return loc

    def clean_title(self):
        title = self.cleaned_data.get("title", "")
        if len(title) > 255:
            raise forms.ValidationError("Le titre ne doit pas dépasser 255 caractères.")
        return title


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({
            "class": "w-full rounded-xl border border-slate-300 bg-transparent px-4 py-3 text-base text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-primary",
            "placeholder": "Email",
        })

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Aucun compte associé à cet email.")
        return email


class PasswordResetConfirmForm(forms.Form):
    code = forms.CharField(
        label="Code",
        max_length=6,
        min_length=6,
        validators=[RegexValidator(r"^\d{6}$", message="Le code doit contenir 6 chiffres.")],
    )
    password1 = forms.CharField(label="Nouveau mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["code"].widget.attrs.update({
            "class": "w-full rounded-full border border-slate-400 px-5 py-3 text-center text-xl tracking-widest text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-primary bg-white",
            "placeholder": "_ _ _ _ _ _",
            "inputmode": "numeric",
            "maxlength": "6",
            "oninput": "this.value=this.value.replace(/[^0-9]/g,'').slice(0,6)",
        })
        base_input = "w-full rounded-full border border-slate-400 px-5 py-3 text-sm md:text-base text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-primary bg-transparent placeholder-slate-500"
        self.fields["password1"].widget.attrs.update({"class": base_input, "placeholder": "Nouveau mot de passe"})
        self.fields["password2"].widget.attrs.update({"class": base_input, "placeholder": "Confirmer"})

    def clean(self):
        cleaned = super().clean()
        pwd1 = cleaned.get("password1")
        pwd2 = cleaned.get("password2")
        if pwd1 and pwd2 and pwd1 != pwd2:
            self.add_error("password2", "Les mots de passe ne correspondent pas.")
        if pwd1 and not _is_strong_password(pwd1):
            self.add_error("password1", "8 caractères min, une majuscule, une minuscule et un caractère spécial.")
        return cleaned
