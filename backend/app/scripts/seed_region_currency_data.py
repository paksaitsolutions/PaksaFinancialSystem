"""
Seed script for regions, countries, and currencies.
"""
from sqlalchemy.orm import Session
from app.core.db.session import SessionLocal
from app.models.region import Region, Country
from app.models.currency import Currency, ExchangeRate
from datetime import date
from decimal import Decimal


def seed_regions(db: Session):
    """Seed initial regions."""
    regions_data = [
        {"code": "NA", "name": "North America", "status": True},
        {"code": "EU", "name": "Europe", "status": True},
        {"code": "AS", "name": "Asia", "status": True},
        {"code": "AF", "name": "Africa", "status": True},
        {"code": "SA", "name": "South America", "status": True},
        {"code": "OC", "name": "Oceania", "status": True},
    ]
    
    for region_data in regions_data:
        existing = db.query(Region).filter(Region.code == region_data["code"]).first()
        if not existing:
            region = Region(**region_data)
            db.add(region)
    
    db.commit()
    print("Regions seeded successfully")


def seed_currencies(db: Session):
    """Seed initial currencies."""
    currencies_data = [
        {"code": "USD", "name": "US Dollar", "symbol": "$", "decimal_places": 2, "is_base_currency": True, "status": "active"},
        {"code": "EUR", "name": "Euro", "symbol": "€", "decimal_places": 2, "is_base_currency": False, "status": "active"},
        {"code": "GBP", "name": "British Pound", "symbol": "£", "decimal_places": 2, "is_base_currency": False, "status": "active"},
        {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "decimal_places": 0, "is_base_currency": False, "status": "active"},
        {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$", "decimal_places": 2, "is_base_currency": False, "status": "active"},
        {"code": "AUD", "name": "Australian Dollar", "symbol": "A$", "decimal_places": 2, "is_base_currency": False, "status": "active"},
        {"code": "CHF", "name": "Swiss Franc", "symbol": "CHF", "decimal_places": 2, "is_base_currency": False, "status": "active"},
        {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥", "decimal_places": 2, "is_base_currency": False, "status": "active"},
        {"code": "INR", "name": "Indian Rupee", "symbol": "₹", "decimal_places": 2, "is_base_currency": False, "status": "active"},
        {"code": "PKR", "name": "Pakistani Rupee", "symbol": "₨", "decimal_places": 2, "is_base_currency": False, "status": "active"},
    ]
    
    for currency_data in currencies_data:
        existing = db.query(Currency).filter(Currency.code == currency_data["code"]).first()
        if not existing:
            currency = Currency(**currency_data)
            db.add(currency)
    
    db.commit()
    print("Currencies seeded successfully")


def seed_countries(db: Session):
    """Seed initial countries."""
    # Get regions
    na_region = db.query(Region).filter(Region.code == "NA").first()
    eu_region = db.query(Region).filter(Region.code == "EU").first()
    as_region = db.query(Region).filter(Region.code == "AS").first()
    
    # Get currencies
    usd = db.query(Currency).filter(Currency.code == "USD").first()
    eur = db.query(Currency).filter(Currency.code == "EUR").first()
    gbp = db.query(Currency).filter(Currency.code == "GBP").first()
    jpy = db.query(Currency).filter(Currency.code == "JPY").first()
    cad = db.query(Currency).filter(Currency.code == "CAD").first()
    pkr = db.query(Currency).filter(Currency.code == "PKR").first()
    inr = db.query(Currency).filter(Currency.code == "INR").first()
    
    countries_data = [
        {
            "code": "US", "code_alpha3": "USA", "name": "United States", 
            "official_name": "United States of America", "region_id": na_region.id if na_region else None,
            "default_currency_id": usd.id if usd else None, "phone_code": "+1",
            "capital": "Washington, D.C.", "timezone": "UTC-5", "status": True
        },
        {
            "code": "CA", "code_alpha3": "CAN", "name": "Canada", 
            "official_name": "Canada", "region_id": na_region.id if na_region else None,
            "default_currency_id": cad.id if cad else None, "phone_code": "+1",
            "capital": "Ottawa", "timezone": "UTC-5", "status": True
        },
        {
            "code": "GB", "code_alpha3": "GBR", "name": "United Kingdom", 
            "official_name": "United Kingdom of Great Britain and Northern Ireland", 
            "region_id": eu_region.id if eu_region else None,
            "default_currency_id": gbp.id if gbp else None, "phone_code": "+44",
            "capital": "London", "timezone": "UTC+0", "status": True
        },
        {
            "code": "DE", "code_alpha3": "DEU", "name": "Germany", 
            "official_name": "Federal Republic of Germany", "region_id": eu_region.id if eu_region else None,
            "default_currency_id": eur.id if eur else None, "phone_code": "+49",
            "capital": "Berlin", "timezone": "UTC+1", "status": True
        },
        {
            "code": "FR", "code_alpha3": "FRA", "name": "France", 
            "official_name": "French Republic", "region_id": eu_region.id if eu_region else None,
            "default_currency_id": eur.id if eur else None, "phone_code": "+33",
            "capital": "Paris", "timezone": "UTC+1", "status": True
        },
        {
            "code": "JP", "code_alpha3": "JPN", "name": "Japan", 
            "official_name": "Japan", "region_id": as_region.id if as_region else None,
            "default_currency_id": jpy.id if jpy else None, "phone_code": "+81",
            "capital": "Tokyo", "timezone": "UTC+9", "status": True
        },
        {
            "code": "PK", "code_alpha3": "PAK", "name": "Pakistan", 
            "official_name": "Islamic Republic of Pakistan", "region_id": as_region.id if as_region else None,
            "default_currency_id": pkr.id if pkr else None, "phone_code": "+92",
            "capital": "Islamabad", "timezone": "UTC+5", "status": True
        },
        {
            "code": "IN", "code_alpha3": "IND", "name": "India", 
            "official_name": "Republic of India", "region_id": as_region.id if as_region else None,
            "default_currency_id": inr.id if inr else None, "phone_code": "+91",
            "capital": "New Delhi", "timezone": "UTC+5:30", "status": True
        },
    ]
    
    for country_data in countries_data:
        existing = db.query(Country).filter(Country.code == country_data["code"]).first()
        if not existing:
            country = Country(**country_data)
            db.add(country)
    
    db.commit()
    print("Countries seeded successfully")


def seed_exchange_rates(db: Session):
    """Seed initial exchange rates."""
    # Get currencies
    usd = db.query(Currency).filter(Currency.code == "USD").first()
    eur = db.query(Currency).filter(Currency.code == "EUR").first()
    gbp = db.query(Currency).filter(Currency.code == "GBP").first()
    jpy = db.query(Currency).filter(Currency.code == "JPY").first()
    pkr = db.query(Currency).filter(Currency.code == "PKR").first()
    
    if not all([usd, eur, gbp, jpy, pkr]):
        print("Some currencies not found, skipping exchange rates")
        return
    
    # Sample exchange rates (USD as base)
    rates_data = [
        {"source_currency_id": usd.id, "target_currency_id": eur.id, "rate": Decimal("0.85"), "effective_date": date.today()},
        {"source_currency_id": usd.id, "target_currency_id": gbp.id, "rate": Decimal("0.73"), "effective_date": date.today()},
        {"source_currency_id": usd.id, "target_currency_id": jpy.id, "rate": Decimal("110.0"), "effective_date": date.today()},
        {"source_currency_id": usd.id, "target_currency_id": pkr.id, "rate": Decimal("280.0"), "effective_date": date.today()},
    ]
    
    for rate_data in rates_data:
        existing = db.query(ExchangeRate).filter(
            ExchangeRate.source_currency_id == rate_data["source_currency_id"],
            ExchangeRate.target_currency_id == rate_data["target_currency_id"],
            ExchangeRate.effective_date == rate_data["effective_date"]
        ).first()
        
        if not existing:
            rate = ExchangeRate(**rate_data)
            db.add(rate)
    
    db.commit()
    print("Exchange rates seeded successfully")


def main():
    """Main seeding function."""
    db = SessionLocal()
    try:
        print("Starting region and currency data seeding...")
        seed_regions(db)
        seed_currencies(db)
        seed_countries(db)
        seed_exchange_rates(db)
        print("All data seeded successfully!")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()