import referenceDataService from '@/services/referenceDataService';

// Cache for reference data
let _currencies: any[] = [];
let _countries: any[] = [];
let _languages: any[] = [];
let _timezones: any[] = [];
let _accountTypes: any[] = [];
let _paymentMethods: any[] = [];
let _taxTypes: any[] = [];
let _bankAccountTypes: any[] = [];

export const getCurrencies = async () => {
  if (_currencies.length === 0) {
    const response = await referenceDataService.getCurrencies();
    _currencies = response.data;
  }
  return _currencies;
};

export const getAccountTypes = async () => {
  if (_accountTypes.length === 0) {
    const response = await referenceDataService.getAccountTypes();
    _accountTypes = response.data;
  }
  return _accountTypes;
};

export const getBankAccountTypes = async () => {
  if (_bankAccountTypes.length === 0) {
    const response = await referenceDataService.getBankAccountTypes();
    _bankAccountTypes = response.data;
  }
  return _bankAccountTypes;
};

export const getPaymentMethods = async () => {
  if (_paymentMethods.length === 0) {
    const response = await referenceDataService.getPaymentMethods();
    _paymentMethods = response.data;
  }
  return _paymentMethods;
};

export const getTaxTypes = async () => {
  if (_taxTypes.length === 0) {
    const response = await referenceDataService.getTaxTypes();
    _taxTypes = response.data;
  }
  return _taxTypes;
};

export const getCountries = async () => {
  if (_countries.length === 0) {
    const response = await referenceDataService.getCountries();
    _countries = response.data;
  }
  return _countries;
};

export const getLanguages = async () => {
  if (_languages.length === 0) {
    const response = await referenceDataService.getLanguages();
    _languages = response.data;
  }
  return _languages;
};

export const getTimezones = async () => {
  if (_timezones.length === 0) {
    const response = await referenceDataService.getTimezones();
    _timezones = response.data;
  }
  return _timezones;
};