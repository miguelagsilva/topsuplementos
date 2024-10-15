from django.views import generic
from django.shortcuts import render

from .models import ProteinPowder, Creatine, PROTEIN_TYPE_CHOICES, CREATINE_TYPE_CHOICES, CREATINE_FORM_CHOICES


def format_product(product):
    if product.weight < 1000:
        product.formatted_weight = f"{product.weight}g"
    elif product.weight % 1000 == 0:
        product.formatted_weight = f"{product.weight // 1000}kg"
    else:
        product.formatted_weight = f"{product.weight / 1000}kg"

    product.formatted_price_per_kg = f"{product.get_price_per_kg():.2f}€/kg"
    product.formatted_price = f"{product.price:.2f}€"


def get_average_price_per_kg(item_list):
    prices = []
    for item in item_list:
        if 100 <= item.weight <= 2500:
            prices.append(item.get_price_per_kg())
    if not prices:
        return item_list[0].get_price_per_kg()

    return sum(prices) / len(prices)


# We need to return a list of creatines that have the format and type
# that was passed in. Each brand may have many products, we want the creatines
# grouped by name, and sorted by price in descending order.
def get_top_creatines(creatine_form, creatine_type):
    all_creatines = Creatine.objects.filter(type=creatine_type, form=creatine_form)

    unique_creatines = {}
    for creatine in all_creatines:
        creatine_code = f"{creatine.brand.code}-{creatine.name}"
        format_product(creatine)
        if creatine_code not in unique_creatines:
            unique_creatines[creatine_code] = []
        unique_creatines[creatine_code].append(creatine)

    for name in unique_creatines:
        unique_creatines[name].sort(key=lambda x: x.price, reverse=True)

    sorted_creatines = sorted(unique_creatines.values(), key=get_average_price_per_kg)

    return sorted_creatines


def get_top_protein_powders(protein_type):
    all_powders = ProteinPowder.objects.filter(type=protein_type)

    unique_powders = {}
    for powder in all_powders:
        powder_code = f"{powder.brand.code}-{powder.name}"
        format_product(powder)
        if powder_code not in unique_powders:
            unique_powders[powder_code] = []
        unique_powders[powder_code].append(powder)

    for name in unique_powders:
        unique_powders[name].sort(key=lambda x: x.price, reverse=True)

    sorted_protein_powders = sorted(unique_powders.values(), key=get_average_price_per_kg)

    return sorted_protein_powders


def protein_powders(request, protein_type=None):
    protein_type_dict = dict(PROTEIN_TYPE_CHOICES)

    if protein_type not in protein_type_dict:
        protein_type = 'concentrate'

    context = {
        'types': protein_type_dict,
        'current_type': [protein_type, protein_type_dict[protein_type]],
        'protein_powders': get_top_protein_powders(protein_type),
    }

    return render(request, 'supplements/protein_powders.html', context)


def creatines(request, creatine_form=None, creatine_type=None):
    creatine_type_dict = dict(CREATINE_TYPE_CHOICES)
    creatine_form_dict = dict(CREATINE_FORM_CHOICES)

    if creatine_form not in creatine_form_dict:
        creatine_form = 'powder'
    if creatine_type not in creatine_type_dict:
        creatine_type = 'monohydrate'

    context = {
        'forms': creatine_form_dict,
        'types': creatine_type_dict,
        'current_form': [creatine_form, creatine_form_dict[creatine_form]],
        'current_type': [creatine_type, creatine_type_dict[creatine_type]],
        'creatines': get_top_creatines(creatine_form, creatine_type),
    }

    return render(request, 'supplements/creatines.html', context)


class IndexView(generic.ListView):
    template_name = "supplements/index.html"
    context_object_name = "protein_powder_list"

    def get_queryset(self):
        protein_powders = ProteinPowder.objects.all()
        sorted_protein_powders = sorted(protein_powders, key=lambda pp: pp.get_price_per_kg())
        return sorted_protein_powders[:20]


class DetailView(generic.DetailView):
    template_name = "supplements/detail.html"
    context_object_name = "protein_powder"

    def get_queryset(self):
        return ProteinPowder.objects
