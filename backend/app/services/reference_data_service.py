"""
Service for managing reference data (countries, currencies, languages, etc.)
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.reference_data import (
    Country, Currency, Language, Timezone, AccountType, 
    PaymentMethod, TaxType, BankAccountType
)
from app.services.base import BaseService


class ReferenceDataService(BaseService):
    """Service for reference data operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, None)  # No primary model
    
    # Countries
    def get_countries(self, active_only: bool = True) -> List[Country]:
        query = self.db.query(Country)
        if active_only:
            query = query.filter(Country.is_active == True)
        return query.order_by(Country.name).all()
    
    def get_country_by_code(self, code: str) -> Optional[Country]:
        return self.db.query(Country).filter(Country.code == code).first()
    
    # Currencies
    def get_currencies(self, active_only: bool = True) -> List[Currency]:
        query = self.db.query(Currency)
        if active_only:
            query = query.filter(Currency.is_active == True)
        return query.order_by(Currency.name).all()
    
    def get_currency_by_code(self, code: str) -> Optional[Currency]:
        return self.db.query(Currency).filter(Currency.code == code).first()
    
    # Languages
    def get_languages(self, active_only: bool = True) -> List[Language]:
        query = self.db.query(Language)
        if active_only:
            query = query.filter(Language.is_active == True)
        return query.order_by(Language.name).all()
    
    def get_language_by_code(self, code: str) -> Optional[Language]:
        return self.db.query(Language).filter(Language.code == code).first()
    
    # Timezones
    def get_timezones(self, active_only: bool = True) -> List[Timezone]:
        query = self.db.query(Timezone)
        if active_only:
            query = query.filter(Timezone.is_active == True)
        return query.order_by(Timezone.name).all()
    
    def get_timezone_by_code(self, code: str) -> Optional[Timezone]:
        return self.db.query(Timezone).filter(Timezone.code == code).first()
    
    # Account Types
    def get_account_types(self, active_only: bool = True) -> List[AccountType]:
        query = self.db.query(AccountType)
        if active_only:
            query = query.filter(AccountType.is_active == True)
        return query.order_by(AccountType.name).all()
    
    def get_account_type_by_code(self, code: str) -> Optional[AccountType]:
        return self.db.query(AccountType).filter(AccountType.code == code).first()
    
    # Payment Methods
    def get_payment_methods(self, active_only: bool = True) -> List[PaymentMethod]:
        query = self.db.query(PaymentMethod)
        if active_only:
            query = query.filter(PaymentMethod.is_active == True)
        return query.order_by(PaymentMethod.name).all()
    
    def get_payment_method_by_code(self, code: str) -> Optional[PaymentMethod]:
        return self.db.query(PaymentMethod).filter(PaymentMethod.code == code).first()
    
    # Tax Types
    def get_tax_types(self, active_only: bool = True) -> List[TaxType]:
        query = self.db.query(TaxType)
        if active_only:
            query = query.filter(TaxType.is_active == True)
        return query.order_by(TaxType.name).all()
    
    def get_tax_type_by_code(self, code: str) -> Optional[TaxType]:
        return self.db.query(TaxType).filter(TaxType.code == code).first()
    
    # Bank Account Types
    def get_bank_account_types(self, active_only: bool = True) -> List[BankAccountType]:
        query = self.db.query(BankAccountType)
        if active_only:
            query = query.filter(BankAccountType.is_active == True)
        return query.order_by(BankAccountType.name).all()
    
    def get_bank_account_type_by_code(self, code: str) -> Optional[BankAccountType]:
        return self.db.query(BankAccountType).filter(BankAccountType.code == code).first()