from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product


PRODUCTS = [
    ("Men’s Trunks & Vests", "trunks", "ARS Signature Stretch Trunk Pack of 3", "ARS-TRK-003", "Soft stretch trunks in a considered three-piece edit.", "95% combed cotton, 5% elastane", "https://lh3.googleusercontent.com/aida-public/AB6AXuD4EUg35u4BnnCPzKHtetIAOUfauSwnzLWi9isoUaKlJ1HHI-5g-TVcsQodWyEyNgT5KJrCo4SphYGP_9NiQBlY2bfe231fZbc5qY0DCgnMZlm1VydbZHC7uu3uvtg4ru1yMKiJW7zS9RkeLaynSi70EViW_Af6SVmYGm9h-p-Q2HKxkYIACTa5WAlwYk6DqQuYeN_u3C_OLgjbFyzHByuA-sFEaZ-Y9KcOUSOKzCDohhjQp6VpEJsQ", "549", "799"),
    ("Women’s Panties & Camisoles", "panties", "Lace-Trim Soft Cotton Briefs", "ARS-PAN-003", "A breathable everyday set with a soft, gentle finish.", "95% combed cotton, 5% elastane", "https://lh3.googleusercontent.com/aida-public/AB6AXuAbNDKqd-2rYrC2_aThQdLn2X7LAJTvFsMuZ2543VbjWJRpkCfP2-wourrxG62IOzVZVhkurN3oN8Db0-CfUvm31dn4XuX9SWVM4zFy6469T85aqKzw1xhndUFVnuJxZbRgFj8lKo0HbBfnxw3PZ6SR2XflTtO0kCWuDMD7SlusDxWsI7Q_skvGqCskwcKnbKWKao_CqOdgdsahDqdYKk4m6xD7J1RNE7YQfoxmFg7I", "499", "699"),
    ("Gift Sets", "gift-sets", "ARS Everyday Essentials Hamper", "ARS-GFT-001", "A thoughtful gift set with our most-loved everyday essentials.", "Combed cotton essentials", "https://lh3.googleusercontent.com/aida-public/AB6AXuBnhEu0OQd1EI2wEHJnwo0IiosjMEaijxwz6u7xd1rZpXqwCdY_Q5al924ZgNInP-GOPcFdxZMdNikOuxdbNtFkOEG8JwvRMtEvKh-1Gc-cnRwAezilS9aFxBp_Kh_Ldaaud3kSfbLERYNK8IU_UkJ1dvol8ZdzOW3ZWYlD_KJZihho_rLZl4D5IHfh9gQRZliHo7eJbiw1Wt-FjwGtXslrPrggWw3xRYwsaMP005I", "899", "1299"),
    ("Men’s Trunks & Vests", "trunks", "Classic Ribbed Cotton Vest", "ARS-VST-001", "A clean essential in soft ribbed combed cotton.", "100% combed cotton", "https://lh3.googleusercontent.com/aida-public/AB6AXuAnYziqmStSSw41Fagw1gSwg_7aTSdauA0E3ggqQJvJWwB9tu2v5vuRqNNW2UfRn2euUQpu5SVyV9AbuHLdnwvn38cgNmfERExdjYk_XeOTVIEmeRzqp908774AcTA2bVIcATRpc8d18PrVZpDnJo7MOGhOASqZuPj8L3OWJPoqRcWFo6uwKlpLiMifFyRhzDCkcdu4q0DSMSjYwICZrLzeB9DaMBnWtEGvuUCWkrE", "299", "399"),
    ("Women’s Panties & Camisoles", "panties", "Modal Lounge Camisole", "ARS-CAM-001", "An easy layer with a smooth hand feel and relaxed drape.", "Modal blend knit", "https://lh3.googleusercontent.com/aida-public/AB6AXuDbrWe-nip_aivKGKZtKRPsP8-LqhV-blCjzVaOE3yPhO632TNwAf91wmWtFdJOSk9Aw4-0HINGCYHzumkT8k32W_oFwnaBxp4XBriOVpkW7S7Bi9mm_U98Fp-pqlGPH7c_a0F_E-_y-U2Uz-ev4PepnSk0gTXmIRGjq1kV86LBTYknWqMzMLbIPSzLq86KUdPeTWttEeGmKw0mpcyhNp0YaoOkTEK6OUdABPYyI", "449", "599"),
    ("Casualwear", "casualwear", "Everyday Heavy Cotton Tee", "ARS-TEE-001", "A relaxed tee with a substantial, soft cotton feel.", "100% combed cotton · 240 GSM", "https://lh3.googleusercontent.com/aida-public/AB6AXuCEOtZINjzreI8jxPO7macDONH87V7IJ3pC1RXw0VJecr_EjtLZvsv7nrS9QdiU8FU2ig2OG4tjDNxWyxsg2ITjnuIacFiwyK4oOvcUQbwm_xztlhd3KN8dYoGrRqKEx7", "799", "1199"),
    ("Women’s Panties & Camisoles", "panties", "Ribbed Everyday Brief", "ARS-PAN-001", "A soft, breathable brief designed for an easy fit.", "95% combed cotton, 5% elastane", "https://lh3.googleusercontent.com/aida-public/AB6AXuAcSlbcN8Ra8THs2Pi2ZUKL044WFs-s_iS-inYsc-3buLE-X3-GpGb78DYQT4zL_oRv8j2GHw7Oi35WgWeuLwldSCij7LhC3IWm3qJ4HDa5OoViEQLBhTw3GISsmW1tvx", "349", "499"),
    ("Gift Sets", "gift-sets", "Tiruppur Classics Gift Box", "ARS-GFT-002", "A ready-to-gift box of dependable everyday favourites.", "Combed cotton essentials", "https://lh3.googleusercontent.com/aida-public/AB6AXuBnhEu0OQd1EI2wEHJnwo0IiosjMEaijxwz6u7xd1rZpXqwCdY_Q5al924ZgNInP-GOPcFdxZMdNikOuxdbNtFkOEG8JwvRMtEvKh-1Gc-cnRwAezilS9aFxBp_Kh_Ldaaud3kSfbLERYNK8IU_UkJ1dvol8ZdzOW3ZWYlD_KJZihho_rLZl4D5IHfh9gQRZliHo7eJbiw1Wt-FjwGtXslrPrggWw3xRYwsaMP005I", "1199", "1499"),
]


class Command(BaseCommand):
    help = "Add the starter ARS Garments product collection (safe to rerun)."
    def handle(self, *args, **options):
        categories = {}
        for label, slug, *_ in PRODUCTS:
            if slug not in categories:
                categories[slug], _ = Category.objects.get_or_create(slug=slug, defaults={"name": label})
        for index, row in enumerate(PRODUCTS):
            category_name, category_slug, name, sku, short, material, image, price, compare = row
            product_slug = slugify(name)
            Product.objects.update_or_create(sku=sku, defaults={
                "category": categories[category_slug], "name": name, "slug": product_slug,
                "short_description": short, "description": "Designed for comfortable daily wear, with careful stitching and considered finishes.",
                "material": material, "image_url": image, "price": Decimal(price),
                "compare_at_price": Decimal(compare), "stock": 30, "is_featured": index < 6, "is_active": True,
            })
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PRODUCTS)} ARS Garments styles."))
