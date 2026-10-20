import os
import django
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solestride.settings')
django.setup()

from django.contrib.auth.models import User
from shop.models import Category, Brand, Shoe, ShoeSize, Order, OrderItem, TrackingUpdate, ShoeReview

def seed():
    print("Clearing old data...")
    ShoeReview.objects.all().delete()
    TrackingUpdate.objects.all().delete()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    ShoeSize.objects.all().delete()
    Shoe.objects.all().delete()
    Category.objects.all().delete()
    Brand.objects.all().delete()

    print("Creating Demo User...")
    demo_user, created = User.objects.get_or_create(
        username="sneakerhead",
        defaults={
            "email": "alex.mercer@example.com",
            "first_name": "Alex",
            "last_name": "Mercer"
        }
    )
    demo_user.set_password("password123")
    demo_user.save()

    print("Creating Categories...")
    cat_running = Category.objects.create(
        name="Performance Running",
        slug="running",
        description="Engineered for marathoners, sprinters, and daily road runners seeking maximum energy return.",
        icon="bi-speedometer2"
    )
    cat_streetwear = Category.objects.create(
        name="Streetwear & Culture",
        slug="streetwear",
        description="Avant-garde silhouettes, chunky soles, and statement kicks for urban culture.",
        icon="bi-fire"
    )
    cat_basketball = Category.objects.create(
        name="Court & Basketball",
        slug="basketball",
        description="High-top ankle stabilization, herringbone multidirectional traction, and explosive bounce.",
        icon="bi-trophy"
    )
    cat_luxury = Category.objects.create(
        name="Luxury & Formal Craft",
        slug="luxury",
        description="Hand-buffed Italian leather, Goodyear welting, and bespoke artisanal footwear.",
        icon="bi-gem"
    )

    print("Creating Brands...")
    b_aerostride = Brand.objects.create(name="AeroStride Labs", slug="aerostride", description="Pioneering aerospace-grade running foam.")
    b_apex = Brand.objects.create(name="Apex Techwear", slug="apex", description="Architectural futuristic street sneakers.")
    b_retrokicks = Brand.objects.create(name="RetroKicks OG", slug="retrokicks", description="Reviving hardwood court classics since 1985.")
    b_solecraft = Brand.objects.create(name="SoleCraft Atelier", slug="solecraft", description="Master leather artisans from Florence and Northampton.")
    b_velox = Brand.objects.create(name="Velox Dynamics", slug="velox", description="Ultra-lightweight sprint and marathon footwear.")

    print("Creating Shoes...")
    shoe1 = Shoe.objects.create(
        title="Nexus Turbo React X-1",
        slug="nexus-turbo-react-x1",
        brand=b_aerostride,
        category=cat_running,
        tagline="Gravity-Defying Energy Return with Dual Carbon Plates",
        description="The Nexus Turbo React X-1 redefines endurance road running. Crafted with our proprietary AeroFiber knit upper and dual carbon-fiber stabilizer plates, every stride propels you forward with 88% mechanical energy return. Neon edge-glow micro-filaments ensure 360-degree night visibility while the segmented nitrogen-infused midsole dampens joint fatigue across 42km marathons.",
        price=Decimal("189.99"),
        original_price=Decimal("249.99"),
        rating=Decimal("4.9"),
        review_count=128,
        image_url="/static/images/shoe_neon_blaze.jpg",
        is_featured=True,
        is_trending=True,
        in_stock=True,
        material="AeroFiber Hydrophobic Mesh & TPU Exo-Cage",
        cushioning="Nitrogen-Infused Dual Carbon React 4D",
        weight="230g / 8.1 oz",
        badge="FLAGSHIP 2026",
    )

    shoe2 = Shoe.objects.create(
        title="Air Royal Heritage High '85",
        slug="air-royal-heritage-high-85",
        brand=b_retrokicks,
        category=cat_basketball,
        tagline="Hardwood Legacy in Full-Grain Royal Obsidian Leather",
        description="Paying homage to the iconic mid-80s championship era, the Air Royal Heritage High '85 preserves authentic collegiate proportions with modernized interior memory foam collar lining. Features full-grain royal blue and polar white leather, encapsulated pressurized air pocket, and non-marking radial cupsole for uncompromising court grip.",
        price=Decimal("220.00"),
        original_price=Decimal("260.00"),
        rating=Decimal("5.0"),
        review_count=94,
        image_url="/static/images/shoe_retro_court.jpg",
        is_featured=True,
        is_trending=True,
        in_stock=True,
        material="100% Full-Grain Aniline Cowhide Leather",
        cushioning="Encapsulated Dual Air-Chamber",
        weight="410g / 14.4 oz",
        badge="COLLECTOR'S EDITION",
    )

    shoe3 = Shoe.objects.create(
        title="Venezia Medallion Brogue Oxford",
        slug="venezia-medallion-brogue-oxford",
        brand=b_solecraft,
        category=cat_luxury,
        tagline="Bespoke Italian Hand-Burnished Calfskin Masterpiece",
        description="Handcrafted in Tuscany by generational cordwainers, each pair of Venezia Oxfords undergoes 180 individual manual steps and a 72-hour burnishing ritual to produce the deep, luminous cognac patina. Constructed with a Goodyear welted leather sole and French calfskin lining, offering lifetime re-soleability and unparalleled formal elegance.",
        price=Decimal("295.00"),
        original_price=Decimal("360.00"),
        rating=Decimal("4.9"),
        review_count=67,
        image_url="/static/images/shoe_luxury_cognac.jpg",
        is_featured=True,
        is_trending=False,
        in_stock=True,
        material="Grade-A Tuscan Hand-Burnished Calfskin",
        cushioning="Corkbed Layer with Stacked Leather Heel",
        weight="380g / 13.4 oz",
        badge="BESPOKE LUXURY",
    )

    shoe4 = Shoe.objects.create(
        title="CyberStrider Triple Stealth 90",
        slug="cyberstrider-triple-stealth-90",
        brand=b_apex,
        category=cat_streetwear,
        tagline="Tactical Cyberpunk Chunky Runner with Neon Pods",
        description="A masterclass in technical streetwear aesthetics. The CyberStrider Triple Stealth features a sculpted multi-density EVA chassis, ballistic cordura panels, and luminescent acid-green air capsules. Built for wet pavement and urban nighttime exploration, fitted with speed-lacing toggles and an ergonomic heel counter.",
        price=Decimal("199.99"),
        original_price=Decimal("235.00"),
        rating=Decimal("4.8"),
        review_count=82,
        image_url="/static/images/shoe_stealth_carbon.jpg",
        is_featured=True,
        is_trending=True,
        in_stock=True,
        material="Ballistic Ripstop Cordura & Molded TPU Shell",
        cushioning="Triple Density EVA with Exposed Gas Cell",
        weight="320g / 11.2 oz",
        badge="STREET ICON",
    )

    shoe5 = Shoe.objects.create(
        title="Atelier Pure White Minimalist Low",
        slug="atelier-pure-white-minimalist-low",
        brand=b_solecraft,
        category=cat_luxury,
        tagline="Quiet Luxury in Monochromatic Nappa Leather",
        description="The ultimate minimalist sneaker. Stripped of loud branding and reduced to pure geometric proportion, the Atelier Pure White is crafted from silky smooth butter-soft calf nappa, stitched Margom-style Italian rubber cupsole, and subtle gold-leaf stamped serial numbering. Pairs effortlessly with tailored trousers or denim.",
        price=Decimal("175.00"),
        original_price=Decimal("210.00"),
        rating=Decimal("4.9"),
        review_count=110,
        image_url="/static/images/shoe_white_minimal.jpg",
        is_featured=False,
        is_trending=True,
        in_stock=True,
        material="Ultra-Fine Nappa Italian Leather",
        cushioning="Removable OrthoLite Hybrid Footbed",
        weight="275g / 9.7 oz",
        badge="BESTSELLER",
    )

    shoe6 = Shoe.objects.create(
        title="Velox Nitro Stride Marathoner",
        slug="velox-nitro-stride-marathoner",
        brand=b_velox,
        category=cat_running,
        tagline="Ultralight Sub-2hr Marathon Competition Shoe",
        description="Designed specifically for world-class racers. Weighing under 200 grams, the Nitro Stride combines supercritical PEBA foam with an aggressive spoon-shaped rocker geometry to maximize forward cadence and minimize calf exertion.",
        price=Decimal("215.00"),
        original_price=Decimal("250.00"),
        rating=Decimal("4.8"),
        review_count=53,
        image_url="/static/images/shoe_neon_blaze.jpg",
        is_featured=False,
        is_trending=False,
        in_stock=True,
        material="Monofilament Featherlight Weave",
        cushioning="Supercritical PEBAX NitroFoam",
        weight="195g / 6.8 oz",
        badge="RACE DAY",
    )

    all_shoes = [shoe1, shoe2, shoe3, shoe4, shoe5, shoe6]

    print("Adding Shoe Sizes...")
    sizes_list = ["7.5", "8.0", "8.5", "9.0", "9.5", "10.0", "10.5", "11.0", "11.5", "12.0"]
    for shoe in all_shoes:
        for sz in sizes_list:
            ShoeSize.objects.create(shoe=shoe, size=sz, stock_quantity=18)

    print("Adding Reviews...")
    ShoeReview.objects.create(
        shoe=shoe1,
        user=demo_user,
        user_name="Marcus Reed (Boston Marathon Finisher)",
        rating=5,
        headline="Cut 4 minutes off my 10K split!",
        comment="The carbon-fiber rebound is instantly noticeable from the very first kilometer. Zero blister hot spots and exceptional toe-box lockdown. SoleStride shipped within 36 hours!",
        verified_purchase=True
    )
    ShoeReview.objects.create(
        shoe=shoe2,
        user=demo_user,
        user_name="Derrick Cole",
        rating=5,
        headline="Craftsmanship matches the original 1985 release",
        comment="The leather grain smells incredible straight out of the matte black collector box. Beautiful stitching and ankle support. Absolute grail pair.",
        verified_purchase=True
    )
    ShoeReview.objects.create(
        shoe=shoe3,
        user=demo_user,
        user_name="Julian Sterling, Esq.",
        rating=5,
        headline="Better than my $800 bespoke benchmades",
        comment="Flawless hand-burnishing. The leather soles broke in within two wears. Perfect for boardroom presentations and black-tie galas.",
        verified_purchase=True
    )

    print("Creating Demo Orders with Active Tracking...")
    order1 = Order.objects.create(
        order_number="SO-98241",
        tracking_code="STRIDE-8842-NY",
        user=demo_user,
        customer_name="Alex Mercer",
        customer_email="alex.mercer@example.com",
        customer_phone="+1 (555) 392-8401",
        shipping_address="742 Evergreen Terrace, Suite 400",
        city="New York",
        postal_code="10001",
        country="United States",
        subtotal=Decimal("409.99"),
        shipping_cost=Decimal("0.00"),
        discount_amount=Decimal("40.00"),
        total_amount=Decimal("369.99"),
        status="OUT_FOR_DELIVERY",
        payment_method="CARD",
        payment_status="PAID",
        courier_partner="FedEx Priority Express (Van #412)",
        current_location="Manhattan Delivery Depot - Route 18",
        driver_name="Devon Wright",
        driver_phone="+1 (800) 492-7102",
        estimated_delivery="Today, by 4:30 PM",
        notes="Customer requested contactless front porch drop-off with photo confirmation."
    )
    OrderItem.objects.create(order=order1, shoe=shoe1, size="10.0", quantity=1, unit_price=shoe1.price)
    OrderItem.objects.create(order=order1, shoe=shoe2, size="10.0", quantity=1, unit_price=shoe2.price)

    TrackingUpdate.objects.create(
        order=order1,
        status_title="Order Verified & Authenticated",
        location="SoleStride JFK Logistics Hub",
        is_completed=True,
        description="Footwear serial tags scanned and authentic holographic seal applied."
    )
    TrackingUpdate.objects.create(
        order=order1,
        status_title="Quality Inspection Cleared",
        location="Quality Lab Bay #2",
        is_completed=True,
        description="Passed 14-point structural stress and aesthetic inspection."
    )
    TrackingUpdate.objects.create(
        order=order1,
        status_title="Dispatched via Air Express",
        location="Regional Sorting Facility - NY",
        is_completed=True,
        description="Package loaded onto flight FS-902 with climate-stabilized shipping container."
    )
    TrackingUpdate.objects.create(
        order=order1,
        status_title="Out for Delivery with Courier",
        location="Midtown West Manhattan",
        is_completed=True,
        description="Driver Devon Wright is currently 4 stops away in FedEx Electric Van #412."
    )

    order2 = Order.objects.create(
        order_number="SO-71539",
        tracking_code="STRIDE-3190-CA",
        user=demo_user,
        customer_name="Alex Mercer",
        customer_email="alex.mercer@example.com",
        customer_phone="+1 (555) 392-8401",
        shipping_address="1200 Wilshire Blvd, Apt 14B",
        city="Los Angeles",
        postal_code="90017",
        country="United States",
        subtotal=Decimal("295.00"),
        shipping_cost=Decimal("0.00"),
        discount_amount=Decimal("0.00"),
        total_amount=Decimal("295.00"),
        status="IN_TRANSIT",
        payment_method="APPLE_PAY",
        payment_status="PAID",
        courier_partner="DHL Express Global Flight",
        current_location="Dallas Sort Facility, Terminal C",
        driver_name="Elena Rostova",
        driver_phone="+1 (800) 332-9182",
        estimated_delivery="Tomorrow by 2:00 PM",
        notes="High value bespoke footwear - Signature required upon handoff."
    )
    OrderItem.objects.create(order=order2, shoe=shoe3, size="9.5", quantity=1, unit_price=shoe3.price)
    TrackingUpdate.objects.create(
        order=order2,
        status_title="Order Confirmed & Payment Captured",
        location="Atelier SoleStride Hub",
        is_completed=True,
        description="Handcrafted pair boxed in cedarwood preservation casing."
    )
    TrackingUpdate.objects.create(
        order=order2,
        status_title="Air Cargo Transit",
        location="Dallas DFW Transit Hub",
        is_completed=True,
        description="En route to Los Angeles International Cargo Bay."
    )

    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed()
