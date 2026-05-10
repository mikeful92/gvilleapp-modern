from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import AddressForm
from .models import Electric, Water

MONTH_ORDER = {
    name: index
    for index, name in enumerate(
        [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ]
    )
}

ADDRESS_TOKENS_TO_DROP = ("GAINESVILLE", "FL", "FLORIDA", ",")
ADDRESS_REPLACEMENTS = {
    "NORTHWEST": "NW",
    "NORTHEAST": "NE",
    "SOUTHWEST": "SW",
    "SOUTHEAST": "SE",
    "TERRACE": "TER",
    "STREET": "ST",
    "AVENUE": "AVE",
    "PLACE": "PL",
    "BOULEVARD": "BLVD",
    "DRIVE": "DR",
    "CIRCLE": "CIR",
    "COURT": "CT",
}


def normalize_address(address: str) -> str:
    address = address.upper()
    for token in ADDRESS_TOKENS_TO_DROP:
        address = address.replace(token, "")
    for full, short in ADDRESS_REPLACEMENTS.items():
        address = address.replace(full, short)
    return " ".join(address.split())


def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html", {"form": AddressForm()})


def results(request: HttpRequest) -> HttpResponse:
    form = AddressForm(request.POST or None)
    context: dict = {"form": form}

    if form.is_valid():
        address = normalize_address(form.cleaned_data["address"])
        context["address"] = address
        electric = sorted(
            Electric.objects.filter(ServiceAddress=address),
            key=lambda r: MONTH_ORDER.get(r.Month, 99),
        )
        water = sorted(
            Water.objects.filter(ServiceAddress=address),
            key=lambda r: MONTH_ORDER.get(r.Month, 99),
        )
        if electric and water:
            context["electricObj"] = electric
            context["waterObj"] = water

    return render(request, "results.html", context)
