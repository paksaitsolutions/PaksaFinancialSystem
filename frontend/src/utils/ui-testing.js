/**
 * UI Testing utilities for GL module components
 */

export class GLUITester {
  /**
   * Test button functionality and styling
   */
  static testButtons(component) {
    const results = {
      buttons: [],
      passed: 0,
      failed: 0
    }

    // Find all buttons in component
    const buttons = component.querySelectorAll('button, .v-btn')
    
    buttons.forEach((button, index) => {
      const test = {
        id: index,
        element: button,
        tests: {
          clickable: button.onclick !== null || button.addEventListener,
          hasIcon: button.querySelector('.v-icon, .mdi') !== null,
          hasText: button.textContent.trim().length > 0,
          hasHover: getComputedStyle(button)[':hover'] !== undefined,
          accessible: button.getAttribute('aria-label') || button.textContent
        }
      }
      
      const passed = Object.values(test.tests).filter(Boolean).length
      test.score = `${passed}/${Object.keys(test.tests).length}`
      
      if (passed >= 3) results.passed++
      else results.failed++
      
      results.buttons.push(test)
    })

    return results
  }

  /**
   * Test form validation and submission
   */
  static testForms(component) {
    const results = {
      forms: [],
      passed: 0,
      failed: 0
    }

    const forms = component.querySelectorAll('form, .v-form')
    
    forms.forEach((form, index) => {
      const inputs = form.querySelectorAll('input, select, textarea, .v-text-field, .v-select')
      const submitBtn = form.querySelector('[type="submit"], .submit-btn')
      
      const test = {
        id: index,
        element: form,
        inputCount: inputs.length,
        tests: {
          hasInputs: inputs.length > 0,
          hasSubmit: submitBtn !== null,
          hasValidation: form.querySelector('.error, .v-messages') !== null,
          hasLabels: form.querySelectorAll('label').length >= inputs.length / 2
        }
      }
      
      const passed = Object.values(test.tests).filter(Boolean).length
      test.score = `${passed}/${Object.keys(test.tests).length}`
      
      if (passed >= 3) results.passed++
      else results.failed++
      
      results.forms.push(test)
    })

    return results
  }

  /**
   * Test table functionality
   */
  static testTables(component) {
    const results = {
      tables: [],
      passed: 0,
      failed: 0
    }

    const tables = component.querySelectorAll('table, .v-data-table')
    
    tables.forEach((table, index) => {
      const headers = table.querySelectorAll('th, .v-data-table-header')
      const rows = table.querySelectorAll('tbody tr, .v-data-table__wrapper tr')
      const pagination = table.querySelector('.v-pagination, .pagination')
      
      const test = {
        id: index,
        element: table,
        tests: {
          hasHeaders: headers.length > 0,
          hasData: rows.length > 0,
          hasPagination: pagination !== null,
          hasSorting: table.querySelector('[data-sortable], .sortable') !== null,
          hasSearch: component.querySelector('.search, .v-text-field') !== null
        }
      }
      
      const passed = Object.values(test.tests).filter(Boolean).length
      test.score = `${passed}/${Object.keys(test.tests).length}`
      
      if (passed >= 3) results.passed++
      else results.failed++
      
      results.tables.push(test)
    })

    return results
  }

  /**
   * Test responsive design
   */
  static testResponsiveness(component) {
    const breakpoints = [
      { name: 'mobile', width: 375 },
      { name: 'tablet', width: 768 },
      { name: 'desktop', width: 1200 }
    ]

    const results = {
      breakpoints: [],
      passed: 0,
      failed: 0
    }

    breakpoints.forEach(bp => {
      // Simulate viewport resize
      Object.defineProperty(window, 'innerWidth', { value: bp.width })
      window.dispatchEvent(new Event('resize'))

      const test = {
        name: bp.name,
        width: bp.width,
        tests: {
          noHorizontalScroll: document.body.scrollWidth <= bp.width,
          elementsVisible: component.offsetHeight > 0,
          textReadable: getComputedStyle(component).fontSize !== '0px',
          buttonsClickable: component.querySelectorAll('button:not([disabled])').length > 0
        }
      }

      const passed = Object.values(test.tests).filter(Boolean).length
      test.score = `${passed}/${Object.keys(test.tests).length}`
      
      if (passed >= 3) results.passed++
      else results.failed++
      
      results.breakpoints.push(test)
    })

    return results
  }

  /**
   * Test accessibility compliance
   */
  static testAccessibility(component) {
    const results = {
      tests: {},
      score: 0,
      issues: []
    }

    // Check for ARIA labels
    const interactiveElements = component.querySelectorAll('button, input, select, textarea, [role="button"]')
    const withAriaLabel = Array.from(interactiveElements).filter(el => 
      el.getAttribute('aria-label') || el.getAttribute('aria-labelledby')
    )
    
    results.tests.ariaLabels = {
      passed: withAriaLabel.length,
      total: interactiveElements.length,
      score: withAriaLabel.length / interactiveElements.length
    }

    // Check color contrast (simplified)
    const textElements = component.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6')
    let contrastIssues = 0
    
    textElements.forEach(el => {
      const style = getComputedStyle(el)
      const color = style.color
      const bgColor = style.backgroundColor
      
      // Simplified contrast check
      if (color === bgColor || (color === 'rgb(0, 0, 0)' && bgColor === 'rgb(0, 0, 0)')) {
        contrastIssues++
      }
    })

    results.tests.colorContrast = {
      issues: contrastIssues,
      total: textElements.length,
      score: 1 - (contrastIssues / textElements.length)
    }

    // Check keyboard navigation
    const focusableElements = component.querySelectorAll(
      'button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
    )
    
    results.tests.keyboardNav = {
      focusableElements: focusableElements.length,
      score: focusableElements.length > 0 ? 1 : 0
    }

    // Calculate overall score
    const scores = Object.values(results.tests).map(test => test.score)
    results.score = scores.reduce((sum, score) => sum + score, 0) / scores.length

    return results
  }

  /**
   * Run comprehensive UI tests
   */
  static runAllTests(component) {
    const results = {
      timestamp: new Date().toISOString(),
      component: component.tagName || 'Unknown',
      tests: {
        buttons: this.testButtons(component),
        forms: this.testForms(component),
        tables: this.testTables(component),
        responsiveness: this.testResponsiveness(component),
        accessibility: this.testAccessibility(component)
      }
    }

    // Calculate overall score
    const testResults = Object.values(results.tests)
    const totalPassed = testResults.reduce((sum, test) => sum + (test.passed || 0), 0)
    const totalTests = testResults.reduce((sum, test) => sum + (test.passed || 0) + (test.failed || 0), 0)
    
    results.overallScore = totalTests > 0 ? (totalPassed / totalTests) * 100 : 0
    results.status = results.overallScore >= 80 ? 'PASS' : 'FAIL'

    return results
  }
}