# Paksa Financial System - QA Issues Tracker

## Testing Protocol
- ✅ = Issue Fixed & Tested
- 🔄 = In Progress
- ❌ = Not Started
- 🧪 = Ready for Testing


## 1. FUNCTIONAL TESTING & FEATURE BEHAVIOR

### 1.1 Missing Authentication Guard for Routes 🧪
**Status:** Ready for Testing  
**Priority:** High  
**Description:** No global route guard enforcing login. Unauthenticated users can manually navigate to protected pages.  
**Location:** `frontend/src/router/index.ts`  
**Test Steps:**
1. Open browser in incognito mode
2. Navigate directly to `http://localhost:3000/dashboard`
3. Verify user is redirected to login page
4. After login, verify user can access protected routes

**Fix Required:**
```javascript
// Add to router/index.ts
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/auth/login')
  } else {
    next()
  }
})
```

---

### 1.2 No Role-Based Route Protection 🧪
**Status:** Ready for Testing  
**Priority:** High  
**Description:** Routes aren't restricted by user roles. Users can manually access admin URLs.  
**Location:** `frontend/src/router/index.ts`  
**Test Steps:**
1. Login as regular user
2. Navigate to `/admin` or `/rbac` directly
3. Verify access is denied or redirected
4. Login as admin and verify access is granted

**Fix Required:**
- Add `meta: { role: 'admin' }` to admin routes
- Implement role checking in navigation guard

---

### 1.3 Partial Responsiveness in UI 🧪
**Status:** Ready for Testing  
**Priority:** Medium  
**Description:** Pages not mobile-friendly, fixed layouts break on smaller screens.  
**Location:** Various views (BudgetView, Dashboard, etc.)  
**Test Steps:**
1. Open app on mobile device or resize browser to 375px width
2. Navigate through all main pages
3. Verify layouts adapt properly
4. Check navigation drawer collapses correctly

---

### 1.4 Insufficient Form Validation & Feedback 🧪
**Status:** Ready for Testing  
**Priority:** Medium  
**Description:** Forms lack robust validation and user feedback.  
**Location:** Various form components  
**Test Steps:**
1. Try submitting forms with empty required fields
2. Enter invalid data (negative numbers, invalid emails)
3. Verify appropriate error messages appear
4. Check loading states during submission

---

### 1.5 Navigation State Sync Issues ✅
**Status:** Complete & Tested  
**Priority:** Low  
**Description:** Sidebar may not highlight correct section on page refresh.  
**Location:** `frontend/src/layouts/MainLayout.vue`  
**Test Steps:**
1. Navigate to a sub-page (e.g., `/gl/accounts`)
2. Refresh the page
3. Verify parent menu is expanded and correct item is highlighted

---

### 1.6 Mock Data and Non-Persistent Actions ❌
**Status:** Not Started  
**Priority:** Low  
**Description:** User interactions appear to work but have no real effect.  
**Location:** Throughout modules  
**Test Steps:**
1. Add/edit records in various modules
2. Refresh page and verify changes persist
3. Check if demo data banners are shown where appropriate

---

## 2. CODE QUALITY ISSUES

### 2.1 Duplicate & Backup Files in Repo ❌
**Status:** Not Started  
**Priority:** Medium  
**Description:** Leftover duplicate files (.bak, .new) in repository.  
**Location:** Various `.bak` and `.new` files  
**Test Steps:**
1. Search for files with `.bak` or `.new` extensions
2. Verify they are removed from repository
3. Check Git history is preserved

---

### 2.2 Inconsistent Project Structure ❌
**Status:** Not Started  
**Priority:** Medium  
**Description:** Mixed structure between `modules/` and `views/` directories.  
**Location:** Project tree structure  
**Test Steps:**
1. Review project structure
2. Verify consistent module organization
3. Check imports still work after restructuring

---

### 2.3 Duplicate Logic Instead of Reuse ❌
**Status:** Not Started  
**Priority:** Medium  
**Description:** Logic repetition across components.  
**Location:** Various modules  
**Test Steps:**
1. Identify repeated patterns
2. Extract to composables or store actions
3. Verify functionality remains the same

---

### 2.4 Large Components Doing Too Much ❌
**Status:** Not Started  
**Priority:** Medium  
**Description:** Components are too large and manage multiple concerns.  
**Location:** Various large component files  
**Test Steps:**
1. Break down large components
2. Verify child components work correctly
3. Check prop passing and events

---

### 2.5 Mixed State Management Approaches ❌
**Status:** Not Started  
**Priority:** Medium  
**Description:** Mix of Pinia and custom state management.  
**Location:** `store/` vs `stores/` directories  
**Test Steps:**
1. Standardize on Pinia
2. Convert auth store to use defineStore
3. Verify state management works consistently

---

### 2.6 Code Style and Naming Conventions ❌
**Status:** Not Started  
**Priority:** Low  
**Description:** Inconsistent naming conventions across files.  
**Location:** Various files  
**Test Steps:**
1. Run ESLint/Prettier
2. Verify consistent naming
3. Remove obsolete config files

---

## 3. PERFORMANCE CONCERNS

### 3.1 No Lazy-Loading of Routes ❌
**Status:** Not Started  
**Priority:** High  
**Description:** All modules bundled together causing heavy initial load.  
**Location:** `frontend/src/router/index.ts`  
**Test Steps:**
1. Check bundle size before fix
2. Implement dynamic imports
3. Verify chunks are created for each module
4. Test initial load time improvement

---

### 3.2 Unoptimized Watchers and Re-computations ❌
**Status:** Not Started  
**Priority:** Medium  
**Description:** Excessive watchers could hurt performance.  
**Location:** Various components with watchers  
**Test Steps:**
1. Profile component re-renders
2. Replace watchers with computed where possible
3. Verify performance improvement

---

### 3.3 Potential Heavy DOM Rendering ❌
**Status:** Not Started  
**Priority:** Medium  
**Description:** Large data tables could cause performance issues.  
**Location:** Data tables in various modules  
**Test Steps:**
1. Load tables with large datasets
2. Implement pagination/virtual scrolling
3. Measure rendering performance

---

### 3.4 Bundle Size and Asset Optimization ❌
**Status:** Not Started  
**Priority:** Medium  
**Description:** Large bundle due to Vuetify + Tailwind CSS.  
**Location:** Build configuration  
**Test Steps:**
1. Analyze bundle size
2. Enable tree-shaking
3. Remove unused dependencies
4. Verify smaller bundle size

---

### 3.5 Handling of Timers and Intervals ❌
**Status:** Not Started  
**Priority:** Low  
**Description:** Potential memory leaks from uncleaned timers.  
**Location:** Components using timers  
**Test Steps:**
1. Check for timer usage
2. Verify cleanup in onBeforeUnmount
3. Test for memory leaks

---

## 4. SECURITY & PERMISSION FLOW

### 4.1 Token Storage Security ❌
**Status:** Not Started  
**Priority:** High  
**Description:** Token storage might be vulnerable to XSS.  
**Location:** `frontend/src/store/auth.ts`  
**Test Steps:**
1. Review token storage method
2. Implement secure storage
3. Test token security

---

### 4.2 Session Expiration Handling ❌
**Status:** Not Started  
**Priority:** High  
**Description:** No automatic session timeout or refresh logic.  
**Location:** API service layer  
**Test Steps:**
1. Let session expire
2. Verify user is redirected to login
3. Test refresh token logic if implemented

---

### 4.3 Frontend Authorization vs. Backend ❌
**Status:** Not Started  
**Priority:** High  
**Description:** Frontend permission checks need backend validation.  
**Location:** Throughout application  
**Test Steps:**
1. Try unauthorized actions via API
2. Verify server-side validation
3. Check error handling in UI

---

### 4.4 Multi-Tenant Data Isolation in UI ❌
**Status:** Not Started  
**Priority:** High  
**Description:** Cached state might show wrong tenant data.  
**Location:** State management  
**Test Steps:**
1. Switch between tenants
2. Verify data is cleared/refreshed
3. Check no cross-tenant data leakage

---

### 4.5 Use of HTTPS and Secure Cookies ❌
**Status:** Not Started  
**Priority:** High  
**Description:** Ensure HTTPS and secure cookies in production.  
**Location:** Deployment configuration  
**Test Steps:**
1. Deploy to staging with HTTPS
2. Verify secure cookies
3. Check CSP headers

---

## Testing Notes

**Before starting any issue:**
1. Create a feature branch
2. Write test cases
3. Implement fix
4. Run tests
5. Update status to 🧪 Ready for Testing

**Testing Requirements:**
- Manual testing steps must pass
- Automated tests should be written where applicable
- Performance improvements should be measurable
- Security fixes should be verified

**Status Updates:**
- Update this file when starting work on an issue
- Mark as 🧪 when ready for testing
- Mark as ✅ only after successful testing
- Add notes about any issues found during testing