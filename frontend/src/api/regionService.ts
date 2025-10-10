/**
 * Region and Country API service
 */
import { api } from './index'

export interface Region {
  id: string
  code: string
  name: string
  status: boolean
  created_at: string
  updated_at: string
}

export interface Country {
  id: string
  code: string
  code_alpha3?: string
  name: string
  official_name?: string
  region_id?: string
  default_currency_id?: string
  phone_code?: string
  status: boolean
  capital?: string
  timezone?: string
  region?: Region
  created_at: string
  updated_at: string
}

export interface RegionCreate {
  code: string
  name: string
  status?: boolean
}

export interface CountryCreate {
  code: string
  code_alpha3?: string
  name: string
  official_name?: string
  region_id?: string
  default_currency_id?: string
  phone_code?: string
  status?: boolean
  capital?: string
  timezone?: string
}

class RegionService {
  // Region methods
  async getRegions(includeInactive = false): Promise<Region[]> {
    const response = await api.get('/regions', {
      params: { include_inactive: includeInactive }
    })
    return response.data
  }

  async getRegion(id: string): Promise<Region> {
    const response = await api.get(`/regions/${id}`)
    return response.data
  }

  async createRegion(data: RegionCreate): Promise<Region> {
    const response = await api.post('/regions', data)
    return response.data
  }

  async updateRegion(id: string, data: Partial<RegionCreate>): Promise<Region> {
    const response = await api.put(`/regions/${id}`, data)
    return response.data
  }

  async deleteRegion(id: string): Promise<void> {
    await api.delete(`/regions/${id}`)
  }

  // Country methods
  async getCountries(includeInactive = false, regionId?: string): Promise<Country[]> {
    const response = await api.get('/countries', {
      params: { 
        include_inactive: includeInactive,
        region_id: regionId
      }
    })
    return response.data
  }

  async getCountry(id: string): Promise<Country> {
    const response = await api.get(`/countries/${id}`)
    return response.data
  }

  async createCountry(data: CountryCreate): Promise<Country> {
    const response = await api.post('/countries', data)
    return response.data
  }

  async updateCountry(id: string, data: Partial<CountryCreate>): Promise<Country> {
    const response = await api.put(`/countries/${id}`, data)
    return response.data
  }

  async deleteCountry(id: string): Promise<void> {
    await api.delete(`/countries/${id}`)
  }
}

export const regionService = new RegionService()