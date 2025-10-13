<template>
  <div class="profile-view">
    <div class="page-header">
      <h1>My Profile</h1>
      <p>Manage your account information and preferences</p>
    </div>

    <div class="profile-content">
      <Card class="profile-card">
        <template #header>
          <div class="profile-header">
            <Avatar :label="userInitials" size="xlarge" class="profile-avatar" />
            <div class="profile-info">
              <h2>{{ user?.full_name || 'User' }}</h2>
              <p>{{ user?.email }}</p>
              <Tag :value="user?.is_superuser ? 'Administrator' : 'User'" :severity="user?.is_superuser ? 'success' : 'info'" />
            </div>
          </div>
        </template>

        <template #content>
          <TabView>
            <TabPanel header="Personal Information">
              <form @submit.prevent="updateProfile" class="profile-form">
                <div class="form-grid">
                  <div class="field">
                    <label for="fullName">Full Name *</label>
                    <InputText id="fullName" v-model="profileForm.full_name" required />
                  </div>
                  <div class="field">
                    <label for="email">Email Address *</label>
                    <InputText id="email" v-model="profileForm.email" type="email" required />
                  </div>
                </div>
                
                <div class="form-grid">
                  <div class="field">
                    <label for="phone">Phone Number</label>
                    <InputText id="phone" v-model="profileForm.phone" />
                  </div>
                  <div class="field">
                    <label for="timezone">Timezone</label>
                    <Dropdown id="timezone" v-model="profileForm.timezone" :options="timezones" optionLabel="label" optionValue="value" />
                  </div>
                </div>

                <div class="form-actions">
                  <Button label="Update Profile" type="submit" :loading="saving" />
                </div>
              </form>
            </TabPanel>

            <TabPanel header="Security">
              <form @submit.prevent="changePassword" class="security-form">
                <div class="field">
                  <label for="currentPassword">Current Password *</label>
                  <Password id="currentPassword" v-model="passwordForm.currentPassword" required />
                </div>
                
                <div class="field">
                  <label for="newPassword">New Password *</label>
                  <Password id="newPassword" v-model="passwordForm.newPassword" required />
                </div>
                
                <div class="field">
                  <label for="confirmPassword">Confirm New Password *</label>
                  <Password id="confirmPassword" v-model="passwordForm.confirmPassword" required />
                </div>

                <div class="form-actions">
                  <Button label="Change Password" type="submit" :loading="changingPassword" />
                </div>
              </form>
            </TabPanel>

            <TabPanel header="Preferences">
              <div class="preferences-form">
                <div class="field">
                  <label for="language">Language</label>
                  <Dropdown id="language" v-model="preferencesForm.language" :options="languages" optionLabel="label" optionValue="value" />
                </div>
                
                <div class="field">
                  <label for="currency">Default Currency</label>
                  <Dropdown id="currency" v-model="preferencesForm.currency" :options="currencies" optionLabel="label" optionValue="value" />
                </div>
                
                <div class="field">
                  <label>Notifications</label>
                  <div class="notification-settings">
                    <div class="field-checkbox">
                      <Checkbox id="emailNotifications" v-model="preferencesForm.emailNotifications" binary />
                      <label for="emailNotifications">Email Notifications</label>
                    </div>
                    <div class="field-checkbox">
                      <Checkbox id="pushNotifications" v-model="preferencesForm.pushNotifications" binary />
                      <label for="pushNotifications">Push Notifications</label>
                    </div>
                  </div>
                </div>

                <div class="form-actions">
                  <Button label="Save Preferences" @click="updatePreferences" :loading="savingPreferences" />
                </div>
              </div>
            </TabPanel>
          </TabView>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotifications } from '@/composables/useNotifications'

const authStore = useAuthStore()
const { success, error } = useNotifications()

const saving = ref(false)
const changingPassword = ref(false)
const savingPreferences = ref(false)

const user = computed(() => authStore.user)

const userInitials = computed(() => {
  return user.value?.full_name?.split(' ').map(n => n[0] || '').join('').toUpperCase() || 'U'
})

const profileForm = ref({
  full_name: '',
  email: '',
  phone: '',
  timezone: 'UTC'
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const preferencesForm = ref({
  language: 'en',
  currency: 'USD',
  emailNotifications: true,
  pushNotifications: false
})

const timezones = [
  { label: 'UTC', value: 'UTC' },
  { label: 'Eastern Time (ET)', value: 'America/New_York' },
  { label: 'Central Time (CT)', value: 'America/Chicago' },
  { label: 'Mountain Time (MT)', value: 'America/Denver' },
  { label: 'Pacific Time (PT)', value: 'America/Los_Angeles' }
]

const languages = [
  { label: 'English', value: 'en' },
  { label: 'Spanish', value: 'es' },
  { label: 'French', value: 'fr' },
  { label: 'German', value: 'de' }
]

const currencies = [
  { label: 'USD - US Dollar', value: 'USD' },
  { label: 'EUR - Euro', value: 'EUR' },
  { label: 'GBP - British Pound', value: 'GBP' },
  { label: 'CAD - Canadian Dollar', value: 'CAD' }
]

onMounted(() => {
  if (user.value) {
    profileForm.value = {
      full_name: user.value.full_name || '',
      email: user.value.email || '',
      phone: '',
      timezone: 'UTC'
    }
  }
})

const updateProfile = async () => {
  saving.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    success('Profile updated successfully')
  } catch (err) {
    error('Failed to update profile')
  } finally {
    saving.value = false
  }
}

const changePassword = async () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    error('New passwords do not match')
    return
  }
  
  changingPassword.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    success('Password changed successfully')
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  } catch (err) {
    error('Failed to change password')
  } finally {
    changingPassword.value = false
  }
}

const updatePreferences = async () => {
  savingPreferences.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    success('Preferences saved successfully')
  } catch (err) {
    error('Failed to save preferences')
  } finally {
    savingPreferences.value = false
  }
}
</script>

<style scoped>
.profile-view {
  padding: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.page-header p {
  margin: 0;
  color: var(--text-color-secondary);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--primary-100) 100%);
}

.profile-avatar {
  background: var(--primary-600) !important;
  color: white !important;
}

.profile-info h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.profile-info p {
  margin: 0 0 1rem 0;
  color: var(--text-color-secondary);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.notification-settings {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-actions {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--surface-200);
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
}
</style>