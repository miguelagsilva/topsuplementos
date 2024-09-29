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
        self.handle_nutrystore()
        self.handle_bulk()
        self.handle_eu_nutrition()
        self.handle_zumub()
        self.handle_prozis()
        self.handle_hsn()
        self.handle_marvelous()
        self.handle_myprotein()
        self.handle_wayup()
        self.handle_masmusculo()
        self.handle_life_pro()

    def handle_zumub(self):
        products = [
            (10328, 2000, "concentrate", 'div.op-price-10328 b.real_price'),
            (10326, 1000, "concentrate", 'div.op-price-10326 b.real_price'),
            (10327, 500, "concentrate", 'div.op-price-10327 b.real_price'),
            (9138, 2000, "isolate", 'div.op-price-9138 b.real_price'),
            (9125, 1000, "isolate", 'div.op-price-9125 b.real_price'),
            (9126, 500, "isolate", 'div.op-price-9126 b.real_price'),
        ]

        for product_id, weight, product_type, price_selector in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_type, brand__code='zumub')
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
            (1854, 16688, 500, "concentrate", 'div#product-price-16688'),
            (3486, 16688, 2000, "concentrate", 'div#product-price-16688'),
            (1854, 12822, 500, "isolate", 'div#product-price-12822'),
            (3486, 12822, 2000, "isolate", 'div#product-price-12822')
        ]

        for button_id, price_id, weight, product_type, price_selector in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_type, brand__code='hsn')
            click_selector = f'label[for="super_attribute[156]_{button_id}"]'
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
