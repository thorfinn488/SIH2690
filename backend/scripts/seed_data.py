import os
import sys

# Add backend root to sys.path so app imports work when script is run
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, engine, Base
from app.models import (
    User, UserRole, Artisan, Buyer, Product, ProductStatus,
    ProductImage, ProductAudio, Catalogue, Pricing,
    MarketOpportunity, OpportunityStatus, AIInsight, AuditLog
)
from app.auth.password_handler import hash_password
from app.ai_mocks.mock_ai_services import calculate_price, explain_price


def seed_database():
    print("Clearing and initializing database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding Users, Artisans, and Buyers...")
        
        # Hashed password for dev accounts
        default_pwd = hash_password("Password123")

        # 1. Admin User
        admin_user = User(
            name="Platform Admin",
            phone="9876543210",
            password_hash=default_pwd,
            role=UserRole.ADMIN,
        )
        db.add(admin_user)

        # 2. 3 Artisans
        artisan1_user = User(
            name="Sunita Devi",
            phone="9811122233",
            password_hash=default_pwd,
            role=UserRole.ARTISAN,
        )
        artisan2_user = User(
            name="Ramesh Kumar",
            phone="9822233344",
            password_hash=default_pwd,
            role=UserRole.ARTISAN,
        )
        artisan3_user = User(
            name="Lakshmi Gowda",
            phone="9833344455",
            password_hash=default_pwd,
            role=UserRole.ARTISAN,
        )
        db.add_all([artisan1_user, artisan2_user, artisan3_user])
        db.commit()

        artisan1 = Artisan(user_id=artisan1_user.id, region="Patiala, Punjab", craft_specialty="Phulkari Embroidery")
        artisan2 = Artisan(user_id=artisan2_user.id, region="Madhubani, Bihar", craft_specialty="Madhubani Folk Painting")
        artisan3 = Artisan(user_id=artisan3_user.id, region="Channapatna, Karnataka", craft_specialty="Wooden Toys & Handicrafts")
        db.add_all([artisan1, artisan2, artisan3])

        # 3. 5 Buyers
        buyers_data = [
            ("FabIndia Sourcing", "9844455566", "FabIndia Retail Ltd.", "Seeking authentic traditional textile crafts for national retail stores."),
            ("Craftsvilla Exports", "9855566677", "Craftsvilla Global", "Procuring handmade folk art and home decor items in bulk quantities."),
            ("Tribal Handicrafts Co-op", "9866677788", "Tribal Craft Collective", "Direct sourcing of eco-friendly bamboo and wooden handicrafts."),
            ("Kala Collective", "9877788899", "Kala Craft Boutique", "Sourcing premium handwoven silks and embroidery dupattas."),
            ("Heritage India Store", "9888899900", "Heritage India Retails", "Looking for certified regional artisan craft catalog items."),
        ]

        buyers = []
        for name, phone, company, reqs in buyers_data:
            u = User(name=name, phone=phone, password_hash=default_pwd, role=UserRole.BUYER)
            db.add(u)
            db.commit()
            b = Buyer(user_id=u.id, company_name=company, requirements=reqs)
            buyers.append(b)
            db.add(b)

        db.commit()

        print("Seeding Products, Catalogues, Pricing, and Images...")

        products_spec = [
            # Artisan 1 - Phulkari & Handwoven
            (artisan1.id, ProductStatus.PUBLISHED, "Handembroidered Phulkari Silk Dupatta", "Textiles & Apparel", "Silk Thread & Cotton", "Phulkari", "Intricately hand-embroidered dupatta featuring traditional geometrical motifs woven by Punjab women artisans.", ["phulkari", "silk", "handwoven"], 600.0, 5, "high"),
            (artisan1.id, ProductStatus.READY, "Handwoven Khadi Cotton Stole", "Textiles & Apparel", "Pure Khadi Cotton", "Handwoven textiles", "Breathable hand-spun khadi cotton stole with fringed borders.", ["khadi", "stole", "cotton"], 350.0, 3, "medium"),
            (artisan1.id, ProductStatus.PROCESSING, "Vintage Phulkari Table Runner", "Home & Living", "Cotton Fabric & Silk", "Phulkari", "Decorative folk embroidery table runner showcasing bright geometric floral patterns.", ["table runner", "phulkari", "decor"], 450.0, 4, "medium"),

            # Artisan 2 - Madhubani & Bamboo
            (artisan2.id, ProductStatus.READY, "Handpainted Madhubani Tree of Life Painting", "Wall Art & Paintings", "Handmade Canvas & Natural Dyes", "Madhubani", "Traditional Madhubani folk painting depicting the sacred Tree of Life and birds.", ["madhubani", "painting", "art"], 500.0, 4, "high"),
            (artisan2.id, ProductStatus.PUBLISHED, "Natural Bamboo Handwoven Table Lamp", "Home & Lighting", "Natural Bamboo", "Bamboo craft", "Eco-friendly handmade bamboo lamp with warm ambient lattice illumination.", ["bamboo", "lamp", "lighting"], 400.0, 3, "medium"),
            (artisan2.id, ProductStatus.DRAFT, "Handmade Bamboo Storage Baskets (Set of 3)", "Home Storage", "Natural Bamboo & Cane", "Bamboo craft", "Set of 3 durable woven bamboo storage baskets.", ["bamboo", "basket", "storage"], 300.0, 2, "low"),

            # Artisan 3 - Wooden Handicrafts
            (artisan3.id, ProductStatus.PUBLISHED, "Channapatna Lacquerware Wooden Nesting Dolls", "Toys & Collectibles", "Soft Wood & Non-Toxic Lacquer", "Wooden handicrafts", "Classic lacquerware wooden nesting dolls crafted using vegetable dyes.", ["channapatna", "wooden toys", "craft"], 350.0, 3, "medium"),
            (artisan3.id, ProductStatus.READY, "Carved Wooden Jewelry Box with Brass Inlay", "Accessories & Storage", "Sheesham Wood & Brass Wire", "Wooden handicrafts", "Elegantly hand-carved wooden jewelry box with brass floral wire inlay.", ["wooden box", "carved", "brass inlay"], 550.0, 5, "high"),
            (artisan3.id, ProductStatus.DRAFT, "Handcarved Wooden Spice Mortar & Pestle", "Kitchenware", "Solid Teak Wood", "Wooden handicrafts", "Traditional durable solid teak wood mortar and pestle set.", ["kitchenware", "wooden", "handmade"], 250.0, 2, "low"),
        ]

        created_products = []
        for (
            art_id, p_status, name, cat, mat, craft, desc, tags, mat_cost, days, complexity
        ) in products_spec:
            p = Product(artisan_id=art_id, status=p_status)
            db.add(p)
            db.commit()
            created_products.append(p)

            # Add sample image
            img = ProductImage(product_id=p.id, url=f"/static/uploads/sample_{p.id[:8]}.jpg")
            db.add(img)

            # Add catalogue entry for READY/PUBLISHED/PROCESSING
            if p_status != ProductStatus.DRAFT:
                cat_entry = Catalogue(
                    product_id=p.id,
                    name=name,
                    category=cat,
                    material=mat,
                    craft=craft,
                    description=desc,
                    tags=tags,
                )
                db.add(cat_entry)

                # Add deterministic pricing
                price_res = calculate_price(mat_cost, days, complexity)
                expl = explain_price(price_res)
                pricing_entry = Pricing(
                    product_id=p.id,
                    suggested_price=price_res["suggested_price"],
                    price_range_low=price_res["price_range"][0],
                    price_range_high=price_res["price_range"][1],
                    explanation=expl,
                )
                db.add(pricing_entry)

        db.commit()

        print("Seeding Market Opportunities...")
        opps_data = [
            (created_products[0].id, buyers[0].id, 95, OpportunityStatus.OPEN),
            (created_products[0].id, buyers[3].id, 88, OpportunityStatus.CONTACTED),
            (created_products[3].id, buyers[1].id, 92, OpportunityStatus.OPEN),
            (created_products[4].id, buyers[2].id, 85, OpportunityStatus.OPEN),
            (created_products[6].id, buyers[4].id, 90, OpportunityStatus.OPEN),
        ]

        for p_id, b_id, score, opp_status in opps_data:
            opp = MarketOpportunity(product_id=p_id, buyer_id=b_id, match_score=score, status=opp_status)
            db.add(opp)

        print("Seeding AI Insights...")
        insights_data = [
            (artisan1.id, "MARKET_DEMAND", "High demand detected for Phulkari embroidery dupattas in Northern urban retail stores."),
            (artisan1.id, "PRICING_TIP", "Increasing silk thread quality enables a 15% higher price range margin."),
            (artisan2.id, "EXPORT_OPPORTUNITY", "Handwoven bamboo home decor items are seeing strong interest from eco-friendly buyers."),
            (artisan3.id, "CATALOG_INSIGHT", "Adding non-toxic dye certification to Channapatna wooden toys boosts buyer trust score by 25%."),
        ]

        for art_id, i_type, msg in insights_data:
            ins = AIInsight(artisan_id=art_id, type=i_type, message=msg)
            db.add(ins)

        db.commit()
        print("Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
