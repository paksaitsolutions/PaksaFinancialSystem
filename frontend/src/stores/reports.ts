import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Report {
  id: string
  name: string
  description: string
  route: string
  icon: string
  category: string
  categoryId?: string
  lastRun?: string
  favorite?: boolean
  is_favorite?: boolean
  tags?: string[]
}

export const useReportsStore = defineStore('reports', () => {
  const reports = ref<Report[]>([])
  const favorites = ref<string[]>([])
  const recentReports = ref<Report[]>([])

  const toggleFavorite = async (reportId: string) => {
    const index = favorites.value.indexOf(reportId)
    if (index > -1) {
      favorites.value.splice(index, 1)
    } else {
      favorites.value.push(reportId)
    }
  }

  const isFavorite = (reportId: string) => {
    return favorites.value.includes(reportId)
  }

  const addToRecent = (report: Report) => {
    const index = recentReports.value.findIndex(r => r.id === report.id)
    if (index > -1) {
      recentReports.value.splice(index, 1)
    }
    recentReports.value.unshift(report)
    if (recentReports.value.length > 10) {
      recentReports.value.pop()
    }
  }

  return {
    reports,
    favorites,
    recentReports,
    toggleFavorite,
    isFavorite,
    addToRecent
  }
})