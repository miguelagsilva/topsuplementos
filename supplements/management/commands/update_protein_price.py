from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from supplements.models import ProteinPowder
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def playwright_request(url, click_selector=None, skip_selectors=None, timeout=2000):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(timeout)

        if skip_selectors:
            for skip_selector in skip_selectors:
                try:
                    page.locator(skip_selector).click()
                    page.wait_for_timeout(timeout)
                except Exception as e:
                    logger.warning(f"Could not click skip element with selector {skip_selector}: {e}")

        if click_selector:
            try:
                page.locator(click_selector).click()
                page.wait_for_timeout(timeout)
            except Exception as e:
                logger.warning(f"Could not click element with selector {click_selector}: {e}")

        html = page.content()
        page.close()
        return BeautifulSoup(html, 'html.parser')


def fetch_and_update_price(product, click_selector=None, skip_selectors=None, price_selector=None):
    price = None

    try:
        soup = playwright_request(product.url, click_selector, skip_selectors)
        price_element = soup.select_one(price_selector)

        if not price_element:
            logger.warning("Price element not found on the page.")
            return

        price = price_processor(price_element)
        product.price = price
        product.save()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return

    logger.info(f"Updated {product.brand.name} {product.name} {product.weight}g protein powder price to {price}")


def price_processor(price_element):
    price_text = price_element.get_text().strip()
    return float(price_text.replace('€', '').replace(',', '.'))


class Command(BaseCommand):
    help = 'Scrape the protein powder price and update the model'

    def handle(self, *args, **options):
        self.handle_zumub()
        self.handle_corposflex()
        self.handle_nutrimania()
        self.handle_nutrystore()
        self.handle_bulk()
        self.handle_eu_nutrition()
        self.handle_prozis()
        self.handle_hsn()
        self.handle_marvelous()
        self.handle_myprotein()
        self.handle_wayup()
        self.handle_masmusculo()
        self.handle_life_pro()
        self.handle_corposflex()

    def handle_zumub(self):
        products = [
            (4730, 1000, "blend", "qnt"),
            (4731, 2200, "blend", "qnt"),
            (7731, 454, "blend", "biotech"),
            (7903, 1000, "blend", "biotech"),
            (7756, 2270, "blend", "biotech"),
            (1937, 900, "blend", "mutant"),
            (1938, 2270, "blend", "mutant"),
            (4351, 4540, "blend", "mutant"),
            (1114, 920, "blend", "scitec_nutrition"),
            (1117, 2350, "blend", "scitec_nutrition"),
            (2085, 5000, "blend", "scitec_nutrition"),
            (10384, 4000, "concentrate", "zumub"),
            (10328, 2000, "concentrate", "zumub"),
            (10326, 1000, "concentrate", "zumub"),
            (10327, 500, "concentrate", "zumub"),
            (9158, 4000, "isolate", "zumub"),
            (9138, 2000, "isolate", "zumub"),
            (9125, 1000, "isolate", "zumub"),
            (9126, 500, "isolate", "zumub"),
        ]

        for product_id, weight, product_type, brand_code in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_type, brand__code=brand_code)
            price_selector = f'div.op-price-{product_id} b.real_price'
            fetch_and_update_price(
                product,
                price_selector=price_selector,
            )

    def handle_prozis(self):
        protein_powders = ProteinPowder.objects.filter(brand__code='prozis')
        price_selector = 'div.line-of-infos p.final-price'

        for protein_powder in protein_powders:
            fetch_and_update_price(
                protein_powder,
                price_selector=price_selector,
            )

    def handle_hsn(self):
        products = [
            (1854, 16688, 500, "concentrate"),
            (3486, 16688, 2000, "concentrate"),
            (1854, 12822, 500, "isolate"),
            (3486, 12822, 2000, "isolate"),
        ]

        for button_id, price_id, weight, product_type in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_type, brand__code='hsn')
            click_selector = f'label[for="super_attribute[156]_{button_id}"]'
            price_selector = f'div#product-price-{price_id}'
            fetch_and_update_price(
                product,
                click_selector=click_selector,
                price_selector=price_selector,
            )

    def handle_marvelous(self):
        product_id = 251
        product = ProteinPowder.objects.get(weight=2000, type="isolate", brand__code='marvelous_nutrition')
        price_selector = f'div.post-{product_id} span.woocommerce-Price-amount bdi'

        fetch_and_update_price(
            product,
            price_selector=price_selector,
        )

    def handle_myprotein(self):
        products = [
            ("250 g", 250, "concentrate"),
            ("1 kg", 1000, "concentrate"),
            ("2.5 kg", 2500, "concentrate"),
            ("5 kg", 5000, "concentrate"),
            ("500 g", 500, "isolate"),
            ("1 kg", 1000, "isolate"),
            ("2.5 kg", 2500, "isolate"),
            ("5 kg", 5000, "isolate")
        ]
        cookie_skip_selector = 'button[id="onetrust-accept-btn-handler"]'
        email_skip_selector = 'button[class="emailReengagement_close_button"]'
        skip_selectors = [cookie_skip_selector, email_skip_selector]
        price_selector = 'p.productPrice_price'

        for aria_label, weight, product_type, price_selector in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_type, brand__code='myprotein')
            click_selector = f'button[aria-label="{aria_label}"]'

            fetch_and_update_price(
                product,
                click_selector=click_selector,
                skip_selectors=skip_selectors,
                price_selector=price_selector,
            )

    def handle_wayup(self):
        product = ProteinPowder.objects.get(weight=1000, type="concentrate", brand__code='wayup')
        price_selector = 'span.theme-money.large-title'

        fetch_and_update_price(
            product,
            price_selector=price_selector,
        )

    def handle_masmusculo(self):
        protein_powders = ProteinPowder.objects.filter(brand__code='masmusculo').union(
            ProteinPowder.objects.filter(brand__code='iron_addict')
        )
        price_selector = 'div.current-price.d-inline span.price'

        for protein_powder in protein_powders:
            fetch_and_update_price(
                protein_powder,
                price_selector=price_selector,
            )

    def handle_life_pro(self):
        protein_powders = ProteinPowder.objects.filter(brand__code='life_pro')
        price_selector = 'span.current-price span.product-price'

        for protein_powder in protein_powders:
            fetch_and_update_price(
                protein_powder,
                price_selector=price_selector,
            )

    def handle_eu_nutrition(self):
        protein_powders = ProteinPowder.objects.filter(brand__code='eu_nutrition')
        price_selector = 'div.product-info-main span.price'

        for protein_powder in protein_powders:
            fetch_and_update_price(
                protein_powder,
                price_selector=price_selector,
            )

    def handle_bulk(self):
        products = [
            (500, "hydrolyzed", "Y29uZmlndXJhYmxlLzE3OS82OQ=="),
            (1000, "hydrolyzed", "Y29uZmlndXJhYmxlLzE3OS8yNQ=="),
            (2500, "hydrolyzed", "Y29uZmlndXJhYmxlLzE3OS8zMw=="),
            (5000, "hydrolyzed", "Y29uZmlndXJhYmxlLzE3OS8zNA=="),
            (500, "clear", "Y29uZmlndXJhYmxlLzE3OS82OQ=="),
            (1000, "clear", "Y29uZmlndXJhYmxlLzE3OS8yNQ=="),
            (2000, "clear", "Y29uZmlndXJhYmxlLzE3OS8xNzg4Nw=="),
            (500, "concentrate", "Y29uZmlndXJhYmxlLzE3OS82OQ=="),
            (1000, "concentrate", "Y29uZmlndXJhYmxlLzE3OS8yNQ=="),
            (2500, "concentrate", "Y29uZmlndXJhYmxlLzE3OS8zMw=="),
            (5000, "concentrate", "Y29uZmlndXJhYmxlLzE3OS8zNA=="),
            (500, "isolate", "Y29uZmlndXJhYmxlLzE3OS82OQ=="),
            (1000, "isolate", "Y29uZmlndXJhYmxlLzE3OS8yNQ=="),
            (2500, "isolate", "Y29uZmlndXJhYmxlLzE3OS8zMw=="),
            (5000, "isolate", "Y29uZmlndXJhYmxlLzE3OS8zNA=="),
        ]
        price_selector = 'span[class="dropin-price dropin-price--default dropin-price--small dropin-price--bold"]'
        skip_selectors = ['button[id="onetrust-accept-btn-handler"]']

        for weight, product_type, label_for_id in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_type, brand__code='bulk')
            click_selector = f'label[for="{label_for_id}"]'
            fetch_and_update_price(
                product,
                click_selector=click_selector,
                price_selector=price_selector,
                skip_selectors=skip_selectors,
            )

    def handle_nutrystore(self):
        products = [
            (45, 900, "blend", "optimum_nutrition"),
            (8, 2270, "blend", "optimum_nutrition"),
        ]

        for product_id, weight, product_type, brand_code in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_type, brand__code=brand_code)
            price_selector = f'div[id="conteudo_preco_{product_id}"] strong'
            fetch_and_update_price(
                product,
                price_selector=price_selector,
            )

    def handle_nutrimania(self):
        products = [
            (450, "concentrate", "sis"),
            (1350, "concentrate", "sis"),
        ]
        price_selector = 'div[class="detalhe_preco"] strong'

        for weight, product_type, brand_code in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_type, brand__code=brand_code)
            fetch_and_update_price(
                product,
                price_selector=price_selector,
            )

    def handle_corposflex(self):
        products = [
            (2270, "isolate", "biotech", "Iso Whey Zero Black"),
            (2270, "isolate", "biotech", "Iso Whey Zero"),
            (1810, "blend", "muscletech", ""),
            (2270, "blend", "muscletech", ""),
            (2200, "hydrolyzed", "dymatize", ""),
        ]
        price_selector = 'div[class="product-options"] span[class="price-new"]'

        for weight, product_type, brand_code, product_name in products:
            product = None
            if product_name != "":
                product = ProteinPowder.objects.get(weight=weight, type=product_type, brand__code=brand_code, name=product_name)
            else:
                product = ProteinPowder.objects.get(weight=weight, type=product_type, brand__code=brand_code)

            fetch_and_update_price(
                product,
                price_selector=price_selector,
            )
