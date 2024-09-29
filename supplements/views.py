from django.views import generic
from django.shortcuts import render

from .models import ProteinPowder, Brand


def get_top_protein_powders(protein_type):
    brands = Brand.objects.all()
    protein_powders = []

    for brand in brands:
        brand_protein_powders = ProteinPowder.objects.filter(brand=brand, type=protein_type)
        unique_powders = {}
        for powder in brand_protein_powders:
            if powder.name not in unique_powders:
                unique_powders[powder.name] = []
            unique_powders[powder.name].append(powder)

        for name, powders in unique_powders.items():
            sorted_powders = sorted(powders, key=lambda x: x.price, reverse=True)[:2]
            protein_powders.append(tuple(sorted_powders))

    # Calculate the average price per kg for weights between 900g and 2.5kg
    def average_price_per_kg(item):
        prices = []
        for pp in item:
            if 900 <= pp.weight <= 2500:
                prices.append(pp.get_price_per_kg())

        if not prices:
            return item[0].get_price_per_kg()

        return sum(prices) / len(prices)

    sorted_protein_powders = sorted(protein_powders, key=average_price_per_kg)

    for item in sorted_protein_powders:
        for protein_powder in item:
            if protein_powder.weight < 1000:
                protein_powder.formatted_weight = f"{protein_powder.weight}g"
            elif protein_powder.weight % 1000 == 0:
                protein_powder.formatted_weight = f"{protein_powder.weight // 1000}kg"
            else:
                protein_powder.formatted_weight = f"{protein_powder.weight / 1000}kg"
            protein_powder.formatted_price_per_kg = f"{protein_powder.get_price_per_kg():.2f}€/kg"
            protein_powder.formatted_price = f"{protein_powder.price:.2f}€"

    return sorted_protein_powders


def protein_powders(request):
    context = {
        'protein_powders': {
            'concentrate_protein_powders': ['Concentrada', get_top_protein_powders('concentrate')],
            'hydrolyzed_protein_powders': ['Hidrolizada', get_top_protein_powders('hydrolyzed')],
            'isolate_protein_powders': ['Isolada', get_top_protein_powders('isolate')],
            'clear_protein_powders': ['Clear', get_top_protein_powders('clear')],
            'blend_protein_powders': ['Clear', get_top_protein_powders('blend')],
        }
    }

    return render(request, 'supplements/protein_powders.html', context)


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
