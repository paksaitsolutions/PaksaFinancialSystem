// Image optimization utilities
export class ImageOptimizer {
  // Lazy load images with intersection observer
  static lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]')
    
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement
          img.src = img.dataset.src!
          img.classList.remove('lazy')
          imageObserver.unobserve(img)
        }
      })
    })

    images.forEach(img => imageObserver.observe(img))
  }

  // Compress image before upload
  static compressImage(file: File, quality: number = 0.8): Promise<Blob> {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')!
      const img = new Image()

      img.onload = () => {
        const { width, height } = img
        canvas.width = width
        canvas.height = height
        
        ctx.drawImage(img, 0, 0, width, height)
        canvas.toBlob(resolve, 'image/jpeg', quality)
      }

      img.src = URL.createObjectURL(file)
    })
  }

  // Generate responsive image URLs
  static getResponsiveImageUrl(baseUrl: string, width: number): string {
    return `${baseUrl}?w=${width}&q=80&f=webp`
  }

  // Preload critical images
  static preloadImages(urls: string[]): Promise<void[]> {
    return Promise.all(
      urls.map(url => new Promise<void>((resolve, reject) => {
        const img = new Image()
        img.onload = () => resolve()
        img.onerror = reject
        img.src = url
      }))
    )
  }
}