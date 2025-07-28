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
          <div v-if="!rail || isMobile" class="logo-text">
            <div class="company-name">Paksa Financial</div>
            <div class="system-name">System</div>
          </div>
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

    <v-list nav density="compact" class="navigation-list" color="primary">
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
        >
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
              :prepend-icon="item.icon"
              class="nav-item nav-item--parent"
              :lines="item.subtitle ? 'two' : undefined"
            >
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
            :prepend-icon="child.icon"
            :disabled="child.disabled"
            class="nav-item nav-item--child"
            rounded="xl"
            :lines="child.subtitle ? 'two' : undefined"
          >
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
        <v-list nav density="compact">
          <v-list-item
            prepend-icon="mdi-help-circle"
            title="Help & Support"
            class="nav-item"
            rounded="xl"
          />
          <v-list-item
            prepend-icon="mdi-logout"
            title="Logout"
            class="nav-item"
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
  padding: 8px 16px;
}

.drawer-footer {
  padding: 16px;
}

@media (max-width: 960px) {
  .navigation-drawer {
    position: fixed !important;
    z-index: 1000;
  }
}
</style>