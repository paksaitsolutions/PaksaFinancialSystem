<template>
  <v-navigation-drawer
    v-model="navigationStore.drawer"
    :rail="isMobile ? false : rail"
    permanent
    :width="280"
    :rail-width="72"
    class="navigation-drawer"
  >
    <template v-slot:prepend>
      <div class="drawer-header">
        <div class="logo-section">
          <v-img
            v-if="!rail || isMobile"
            src="/logo.svg"
            alt="Paksa Financial"
            height="32"
            width="32"
            class="logo"
          />
          <transition name="fade">
            <div v-if="!rail || isMobile" class="logo-text">
              <div class="company-name">Paksa Financial</div>
              <div class="system-name">Enterprise System</div>
            </div>
          </transition>
        </div>
        <v-btn
          v-if="!isMobile"
          icon
          variant="text"
          size="small"
          @click="rail = !rail"
          class="rail-toggle"
        >
          <v-icon>{{ rail ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>
        </v-btn>
      </div>
    </template>

    <v-list nav density="comfortable" class="navigation-list" color="primary" active-color="primary" item-props>
      <template v-for="item in navigationStore.items" :key="item.title">
        <!-- Single item -->
        <v-list-item
          v-if="!item.children"
          :to="item.to"
          :prepend-icon="item.icon"
          :disabled="item.disabled"
          class="nav-item"
          rounded="xl"
          :lines="item.subtitle ? 'two' : undefined"
          active-class="active-nav-item"
        >
          <template #prepend>
            <v-icon size="22" class="nav-icon">{{ item.icon }}</v-icon>
          </template>
          <template #default>
            <v-list-item-title>{{ item.title }}</v-list-item-title>
            <v-list-item-subtitle v-if="item.subtitle">{{ item.subtitle }}</v-list-item-subtitle>
          </template>
          <template v-if="item.badge" #append>
            <v-badge :content="item.badge" color="error" />
          </template>
        </v-list-item>

        <!-- Group with children -->
        <v-list-group v-else :value="item.title" class="nav-group">
          <template #activator="{ props }">
            <v-list-item
              v-bind="props"
              class="nav-item nav-item--parent"
              :lines="item.subtitle ? 'two' : undefined"
              active-class="active-nav-item"
            >
              <template #prepend>
                <v-icon size="22" class="nav-icon">{{ item.icon }}</v-icon>
              </template>
              <template #default>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
                <v-list-item-subtitle v-if="item.subtitle">{{ item.subtitle }}</v-list-item-subtitle>
              </template>
            </v-list-item>
          </template>

          <v-list-item
            v-for="child in item.children"
            :key="child.title"
            :to="child.to"
            :disabled="child.disabled"
            class="nav-item nav-item--child"
            rounded="xl"
            :lines="child.subtitle ? 'two' : undefined"
            active-class="active-nav-item"
          >
            <template #prepend>
              <v-icon size="20" class="nav-icon">{{ child.icon }}</v-icon>
            </template>
            <template #default>
              <v-list-item-title>{{ child.title }}</v-list-item-title>
              <v-list-item-subtitle v-if="child.subtitle">{{ child.subtitle }}</v-list-item-subtitle>
            </template>
            <template v-if="child.badge" #append>
              <v-badge :content="child.badge" color="error" />
            </template>
          </v-list-item>
        </v-list-group>
      </template>
    </v-list>

    <template v-slot:append>
      <div class="drawer-footer">
        <v-divider class="mb-2" />
        <v-list nav density="compact" class="footer-list">
          <v-list-item
            prepend-icon="mdi-help-circle"
            title="Help & Support"
            class="footer-item"
            rounded="xl"
          />
          <v-list-item
            prepend-icon="mdi-logout"
            title="Logout"
            class="footer-item"
            rounded="xl"
            @click="logout"
          />
        </v-list>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNavigationStore } from '@/stores/navigation'
import { useResponsive } from '@/composables/useResponsive'

const router = useRouter()
const navigationStore = useNavigationStore()
const { isMobile } = useResponsive()

const rail = ref(false)

const logout = () => {
  // Handle logout logic
  router.push('/auth/login')
}
</script>

<style scoped>
.navigation-drawer {
  border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.company-name {
  font-size: 16px;
  font-weight: 600;
  color: rgb(var(--v-theme-primary));
}

.system-name {
  font-size: 12px;
  color: rgb(var(--v-theme-on-surface-variant));
}

.rail-toggle {
  opacity: 0.7;
  transition: opacity 0.2s;
}

.rail-toggle:hover {
  opacity: 1;
}

.navigation-list {
  padding: 8px 8px 8px 0;
}

.nav-item {
  margin-bottom: 4px;
  border-radius: 12px !important;
  min-height: 48px;
}

.nav-item--parent {
  font-weight: 500;
}

.nav-item--child {
  margin-left: 16px;
  font-size: 14px;
}

.nav-group {
  margin-bottom: 8px;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.active-nav-item {
  background-color: #1976d2 !important;
  color: #fff !important;
}
.active-nav-item .v-list-item-title,
.active-nav-item .v-list-item-subtitle,
.active-nav-item .v-icon {
  color: #fff !important;
}

.drawer-footer {
  padding: 16px 8px 8px 0;
}
.footer-list {
  padding: 0;
}
.footer-item {
  border-radius: 12px !important;
  margin-bottom: 4px;
}

@media (max-width: 960px) {
  .navigation-drawer {
    position: fixed !important;
    z-index: 1000;
  }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>