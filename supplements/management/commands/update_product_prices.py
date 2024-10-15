import logging
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from webdriver_manager.firefox import GeckoDriverManager
from urllib3.exceptions import NewConnectionError

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from supplements.models import ProteinPowder, Creatine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
options = Options()
#options.add_argument("--headless")  # Run in headless mode, comment out for debugging
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(service=service, options=options)


def selenium_request(url, click_selector=None, skip_selectors=None, timeout=4000):
    driver.get(url)
    driver.implicitly_wait(timeout)

    if skip_selectors:
        for skip_selector in skip_selectors:
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, skip_selector))
                )
                driver.execute_script("arguments[0].click();", element)
            except Exception as e:
                logger.warning(f"Could not click skip element with selector {skip_selector}: {e}")

    if click_selector:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, click_selector))
            )
            driver.execute_script("arguments[0].click();", element)
        except ElementClickInterceptedException:
            logger.warning(f"Element with selector {click_selector} was intercepted. Trying to click using JavaScript.")
            element = driver.find_element(By.CSS_SELECTOR, click_selector)
            driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            logger.warning(f"Could not click element with selector {click_selector}: {e}")

    html = driver.page_source
    return BeautifulSoup(html, 'html.parser')


def fetch_and_update_price(product, click_selector=None, skip_selectors=None, price_selector=None):
    price = None
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            soup = selenium_request(product.url, click_selector, skip_selectors)
            price_element = soup.select_one(price_selector)

            if not price_element:
                logger.warning("Price element not found on the page.")
                return

            price = price_processor(price_element)
            product.price = price
            product.save()
            break
        except NewConnectionError:
            if attempt < max_retries - 1:
                logger.warning(f"Connection error. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Unable to connect.")
                return
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return

    if price:
        logger.info(f"Updated {product.brand.name} {product.name} {product.weight}g protein powder price to {price}")
    else:
        logger.warning(f"Failed to update price for {product.brand.name} {product.name} {product.weight}g protein powder")


def price_processor(price_element):
    price_text = price_element.get_text().strip()
    return float(price_text.replace('€', '').replace(',', '.'))


class Command(BaseCommand):
    help = 'Scrape the products webpages and update the model'

    def handle(self, *args, **options):
        self.handle_zumub()
        self.handle_hsn()
        self.handle_corposflex()
        self.handle_nutrimania()
        self.handle_nutrystore()
        self.handle_bulk()
        self.handle_eu_nutrition()
        self.handle_prozis()
        self.handle_marvelous()
        self.handle_myprotein()
        self.handle_wayup()
        self.handle_masmusculo()
        self.handle_life_pro()
        self.handle_corposflex()
        driver.quit()

    def handle_zumub(self):
        products = [
            ("creatine", 633, 63, "capsules", "creapure", "reflex", None),
            ("creatine", 3550, 540, "capsules", "monohydrate", "activlab", None),
            ("creatine", 3549, 216, "capsules", "monohydrate", "activlab", None),
            ("creatine", 20240, 405, "capsules", "monohydrate", "zumub", None),
            ("creatine", 20239, 270, "capsules", "monohydrate", "zumub", None),
            ("creatine", 20238, 135, "capsules", "monohydrate", "zumub", None),
            ("creatine", 2599, 194, "capsules", "monohydrate", "scitec_nutrition", None),
            ("creatine", 2600, 300, "powder", "monohydrate", "scitec_nutrition", None),
            ("creatine", 1855, 300, "powder", "micronised", "biotech", "Tri Creatine Malate"),
            ("creatine", 631, 250, "powder", "monohydrate", "reflex", None),
            ("creatine", 632, 500, "powder", "monohydrate", "reflex", None),
            ("creatine", 2512, 500, "powder", "monohydrate", "animal", None),
            ("creatine", 22588, 100, "powder", "monohydrate", "zumub", "Creatine Monohydrate Professional"),
            ("creatine", 16199, 500, "powder", "monohydrate", "zumub", "Creatine Monohydrate Professional"),
            ("creatine", 1850, 300, "powder", "micronised", "biotech", "100% Creatine Monohydrate"),
            ("creatine", 8490, 300, "powder", "creapure", "dymatize", None),
            ("creatine", 8096, 500, "powder", "creapure", "dymatize", None),
            ("creatine", 9182, 100, "powder", "monohydrate", "zumub", "Creatine Monohydrate"),
            ("creatine", 22588, 250, "powder", "monohydrate", "zumub", "Creatine Monohydrate"),
            ("creatine", 7141, 500, "powder", "monohydrate", "zumub", "Creatine Monohydrate"),
            ("creatine", 7186, 1000, "powder", "monohydrate", "zumub", "Creatine Monohydrate"),
            ("creatine", 24947, 500, "powder", "creapure", "zumub", None),
            ("creatine", 25470, 1000, "powder", "creapure", "zumub", None),
            ("creatine", 12609, 300, "powder", "monohydrate", "ostrovit", None),
            ("creatine", 10207, 500, "powder", "monohydrate", "ostrovit", None),
            ("creatine", 732, 317, "powder", "micronised", "optimum_nutrition", None),
            ("creatine", 2679, 634, "powder", "micronised", "optimum_nutrition", None),
            ("protein_powder", 4730, 1000, "powder", "blend", "qnt", None),
            ("protein_powder", 4731, 2200, "powder", "blend", "qnt", None),
            ("protein_powder", 7731, 454, "powder", "blend", "biotech", None),
            ("protein_powder", 7903, 1000, "powder", "blend", "biotech", None),
            ("protein_powder", 7756, 2270, "powder", "blend", "biotech", None),
            ("protein_powder", 1937, 900, "powder", "blend", "mutant", None),
            ("protein_powder", 1938, 2270, "powder", "blend", "mutant", None),
            ("protein_powder", 4351, 4540, "powder", "blend", "mutant", None),
            ("protein_powder", 1114, 920, "powder", "blend", "scitec_nutrition", None),
            ("protein_powder", 1117, 2350, "powder", "blend", "scitec_nutrition", None),
            ("protein_powder", 2085, 5000, "powder", "blend", "scitec_nutrition", None),
            ("protein_powder", 10384, 4000, "powder", "concentrate", "zumub", None),
            ("protein_powder", 10328, 2000, "powder", "concentrate", "zumub", None),
            ("protein_powder", 10326, 1000, "powder", "concentrate", "zumub", None),
            ("protein_powder", 10327, 500, "powder", "concentrate", "zumub", None),
            ("protein_powder", 9158, 4000, "powder", "isolate", "zumub", None),
            ("protein_powder", 9138, 2000, "powder", "isolate", "zumub", None),
            ("protein_powder", 9125, 1000, "powder", "isolate", "zumub", None),
            ("protein_powder", 9126, 500, "powder", "isolate", "zumub", None),
        ]

        for product_type, product_id, weight, product_form, product_variant, brand_code, product_name in products:
            try:
                if product_type == "protein_powder":
                    if product_name:
                        product = ProteinPowder.objects.get(
                            weight=weight,
                            type=product_variant,
                            form=product_form,
                            brand__code=brand_code,
                            name=product_name
                        )
                    else:
                        product = ProteinPowder.objects.get(
                            weight=weight,
                            type=product_variant,
                            form=product_form,
                            brand__code=brand_code,
                        )
                elif product_type == "creatine":
                    if product_name:
                        product = Creatine.objects.get(
                            weight=weight,
                            type=product_variant,
                            form=product_form,
                            brand__code=brand_code,
                            name=product_name
                        )
                    else:
                        product = Creatine.objects.get(
                            weight=weight,
                            type=product_variant,
                            form=product_form,
                            brand__code=brand_code,
                        )
                price_selector = f'div[data-pid="{product_id}"] b.real_price'
                fetch_and_update_price(
                    product,
                    price_selector=price_selector,
                )
            except ObjectDoesNotExist:
                logger.warning(f"Product not found: {product_type}, {weight}g, {product_variant}, {product_form}, {brand_code}, {product_name}")
                continue

    def handle_prozis(self):
        products = ProteinPowder.objects.filter(brand__code='prozis').union(Creatine.objects.filter(brand__code='prozis'))
        price_selector = 'div.line-of-infos p.final-price'

        for product in products:
            fetch_and_update_price(
                product,
                price_selector=price_selector,
            )

    def handle_hsn(self):
        products = [
            (1854, 16688, 500, "concentrate"),
            (3486, 16688, 2000, "concentrate"),
            (1854, 12822, 500, "isolate"),
            (3486, 12822, 2000, "isolate"),
        ]

        for button_id, price_id, weight, product_variant in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_variant, brand__code='hsn')
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

        for aria_label, weight, product_variant, price_selector in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_variant, brand__code='myprotein')
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

        for weight, product_variant, label_for_id in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_variant, brand__code='bulk')
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

        for product_id, weight, product_variant, brand_code in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_variant, brand__code=brand_code)
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

        for weight, product_variant, brand_code in products:
            product = ProteinPowder.objects.get(weight=weight, type=product_variant, brand__code=brand_code)
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

        for weight, product_variant, brand_code, product_name in products:
            product = None
            if product_name != "":
                product = ProteinPowder.objects.get(weight=weight, type=product_variant, brand__code=brand_code, name=product_name)
            else:
                product = ProteinPowder.objects.get(weight=weight, type=product_variant, brand__code=brand_code)

            fetch_and_update_price(
                product,
                price_selector=price_selector,
            )
