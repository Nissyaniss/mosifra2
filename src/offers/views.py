from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView

from accounts.models import Offer, CompanyProfile, InstitutionProfile
from accounts.forms import OfferForm
from accounts.countries import get_country_search_names


class CreateOfferView(LoginRequiredMixin, FormView):
    template_name = "offers/create_offer.html"
    form_class = OfferForm
    success_url = reverse_lazy("profiles:my_offers")

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ("company", "institution"):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, "company_profile", None) or getattr(self.request.user, "institution_profile", None)
        context["company_location"] = profile.location if profile else ""
        return context

    def form_valid(self, form):
        offer = form.save(commit=False)
        offer.company = self.request.user
        offer.save()
        messages.success(self.request, "L'offre a été publiée")
        return super().form_valid(form)


class OfferDetailView(LoginRequiredMixin, TemplateView):
    template_name = "offers/offer_detail_private.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ("company", "institution"):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offer = get_object_or_404(Offer, pk=self.kwargs["offer_id"], company=self.request.user)
        profile = getattr(self.request.user, "company_profile", None) or getattr(self.request.user, "institution_profile", None)
        context["offer"] = offer
        context["company"] = profile
        return context


class EditOfferView(LoginRequiredMixin, UpdateView):
    model = Offer
    form_class = OfferForm
    template_name = "offers/edit_offer.html"
    pk_url_kwarg = "offer_id"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in ("company", "institution"):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Offer.objects.filter(company=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = getattr(self.request.user, "company_profile", None) or getattr(self.request.user, "institution_profile", None)
        context["company_location"] = profile.location if profile else ""
        return context

    def get_success_url(self):
        return reverse_lazy("offers:detail", kwargs={"offer_id": self.object.pk})


class OffersListView(TemplateView):
    template_name = "offers/offers_list.html"

    def _get_searchable_location(self, offer):
        profile = getattr(offer.company, "company_profile", None) or getattr(offer.company, "institution_profile", None)
        parts = []
        if offer.location:
            parts.append(offer.location.lower())
        if profile and profile.country_code:
            names = get_country_search_names(profile.country_code)
            parts.extend(names)
        return " ".join(parts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        location = self.request.GET.get("location", "").strip()

        offers = Offer.objects.select_related("company").order_by("-created_at")

        if query:
            offers = offers.filter(
                Q(title__icontains=query) |
                Q(skills__icontains=query) |
                Q(description__icontains=query) |
                Q(contract_type__icontains=query) |
                Q(company__company_profile__organisation_name__icontains=query) |
                Q(company__institution_profile__organisation_name__icontains=query)
            )

        all_offers = list(offers)

        if location:
            terms = location.lower().split()
            filtered_offers = []
            for offer in all_offers:
                searchable = self._get_searchable_location(offer)
                if all(term in searchable for term in terms):
                    filtered_offers.append(offer)
            all_offers = filtered_offers

        offers_with_logo = []
        for offer in all_offers:
            profile = getattr(offer.company, "company_profile", None) or getattr(offer.company, "institution_profile", None)
            logo_url = profile.logo.url if profile and profile.logo else None
            company_name = profile.organisation_name if profile else ""
            offers_with_logo.append({
                "offer": offer,
                "logo_url": logo_url,
                "company_name": company_name,
            })

        context["offers"] = offers_with_logo
        context["count"] = len(offers_with_logo)
        context["query"] = query
        context["location"] = location
        return context


class PublicOfferDetailView(TemplateView):
    template_name = "offers/offer_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        offer_id = self.kwargs.get("pk")
        offer = get_object_or_404(Offer, pk=offer_id)
        profile = getattr(offer.company, "company_profile", None) or getattr(offer.company, "institution_profile", None)
        context["offer"] = offer
        context["company"] = profile
        return context
