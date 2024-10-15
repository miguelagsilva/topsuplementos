from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    website_url = models.URLField()

    def __str__(self):
        return self.name


PROTEIN_TYPE_CHOICES = [
    ('concentrate', 'Concentrado'),
    ('isolate', 'Isolado'),
    ('clear', 'Clear'),
    ('blend', 'Blend'),
]


class ProteinPowder(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    weight = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(
        max_length=20,
        choices=PROTEIN_TYPE_CHOICES,
    )
    image = models.ImageField(upload_to='protein_powders')
    url = models.URLField()

    def __str__(self):
        return self.name

    def get_price_per_kg(self):
        return float("{:.2f}".format(float(self.price) / (self.weight / 1000)))


CREATINE_TYPE_CHOICES = [
    ('monohydrate', 'Monohidratada'),
    ('creapure', 'Creapure®'),
    ('micronised', 'Micronizada')
]
CREATINE_FORM_CHOICES = [
    ('powder', 'Pó'),
    ('capsules', 'Cápsulas'),
]


class Creatine(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    weight = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(
        max_length=20,
        choices=CREATINE_TYPE_CHOICES,
    )
    form = models.CharField(
        max_length=20,
        choices=CREATINE_FORM_CHOICES,
    )
    capsule_amount = models.PositiveIntegerField(null=True, blank=True)
    capsule_weight = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='protein_powders')
    url = models.URLField()

    def __str__(self):
        return self.name

    def get_price_per_kg(self):
        return float("{:.2f}".format(float(self.price) / (self.weight / 1000)))
