import logging
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from django.core.management.base import BaseCommand

from supplements.models import Creatine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def playwright_request(url, click_selector=None, skip_selectors=None, timeout=4000):
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


def fetch_product_data(url, selectors, click_selector=None, skip_selectors=None):
    try:
        soup = playwright_request(url, click_selector, skip_selectors)
        product_data = {}

        for field, selector in selectors.items():
            element = soup.select_one(selector)
            if not element:
                logger.warning(f"{field.capitalize()} element not found on the page.")
                product_data[field] = None
            else:
                product_data[field] = element.get_text().strip()

        return product_data
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


def create_product(product_type, product_data):
    product = Creatine(
            name=product_data['name'],
            brand=product_data['brand'],
            price=float(product_data['price'].replace('€', '').replace(',', '.')),
            weight=int(product_data['weight']),
            url=product_data['url']
    )

    #product.save()
    logger.info(f"Created {product_type}: {product.brand} {product.name} {product.weight}g")
    return product


class Command(BaseCommand):
    help = 'Scrape a webpage to create a model'

    def handle(self, *args, **options):
        url = args[0]
        print(url)
        self.handle_prozis(url)

    def handle_prozis(self, url):
        selectors = {
            'name': 'h1.product-name',
            'brand': 'h2.product-brand',
            'price': 'span.price',
            'weight': 'span.weight',
        }
        product_data = fetch_product_data(url, selectors, click_selector='a.btn-primary')
        if product_data:
            product_data['url'] = url
            #product = create_product(product_type, product_data)
        else:
            logger.error("Failed to fetch product data")
