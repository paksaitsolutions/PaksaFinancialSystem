<template>
  <v-dialog v-model="dialog" max-width="500px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">Change Password</span>
      </v-card-title>
      
      <v-card-text>
        <v-form ref="passwordForm" @submit.prevent="changePassword">
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="passwordData.old_password"
                label="Current Password"
                type="password"
                :rules="[v => !!v || 'Current password is required']"
                required
              ></v-text-field>
            </v-col>
            
            <v-col cols="12">
              <v-text-field
                v-model="passwordData.new_password"
                label="New Password"
                type="password"
                :rules="passwordRules"
                @input="validateNewPassword"
                required
              ></v-text-field>
              
              <!-- Password Strength Indicator -->
              <div v-if="passwordData.new_password" class="mt-2">
                <v-progress-linear
                  :model-value="passwordStrength.score"
                  :color="passwordStrength.color"
                  height="6"
                ></v-progress-linear>
                <div class="text-caption mt-1">
                  Strength: {{ passwordStrength.strength }}
                </div>
                <div v-if="passwordStrength.feedback.length > 0" class="text-caption text-warning mt-1">
                  <ul class="pl-4">
                    <li v-for="tip in passwordStrength.feedback" :key="tip">{{ tip }}</li>
                  </ul>
                </div>
              </div>
            </v-col>
            
            <v-col cols="12">
              <v-text-field
                v-model="confirmPassword"
                label="Confirm New Password"
                type="password"
                :rules="[
                  v => !!v || 'Please confirm your password',
                  v => v === passwordData.new_password || 'Passwords do not match'
                ]"
                required
              ></v-text-field>
            </v-col>
            
            <!-- Password Policy Requirements -->
            <v-col cols="12" v-if="policy">
              <v-card variant="outlined" class="pa-3">
                <div class="text-subtitle2 mb-2">Password Requirements:</div>
                <div class="text-caption">
                  <v-icon 
                    :color="passwordData.new_password.length >= policy.min_length ? 'success' : 'error'" 
                    size="small"
                  >
                    {{ passwordData.new_password.length >= policy.min_length ? 'mdi-check' : 'mdi-close' }}
                  </v-icon>
                  At least {{ policy.min_length }} characters
                </div>
                <div class="text-caption" v-if="policy.require_uppercase">
                  <v-icon 
                    :color="/[A-Z]/.test(passwordData.new_password) ? 'success' : 'error'" 
                    size="small"
                  >
                    {{ /[A-Z]/.test(passwordData.new_password) ? 'mdi-check' : 'mdi-close' }}
                  </v-icon>
                  One uppercase letter
                </div>
                <div class="text-caption" v-if="policy.require_lowercase">
                  <v-icon 
                    :color="/[a-z]/.test(passwordData.new_password) ? 'success' : 'error'" 
                    size="small"
                  >
                    {{ /[a-z]/.test(passwordData.new_password) ? 'mdi-check' : 'mdi-close' }}
                  </v-icon>
                  One lowercase letter
                </div>
                <div class="text-caption" v-if="policy.require_numbers">
                  <v-icon 
                    :color="/\d/.test(passwordData.new_password) ? 'success' : 'error'" 
                    size="small"
                  >
                    {{ /\d/.test(passwordData.new_password) ? 'mdi-check' : 'mdi-close' }}
                  </v-icon>
                  One number
                </div>
                <div class="text-caption" v-if="policy.require_special_chars">
                  <v-icon 
                    :color="/[!@#$%^&*(),.?\":{}|<>]/.test(passwordData.new_password) ? 'success' : 'error'" 
                    size="small"
                  >
                    {{ /[!@#$%^&*(),.?\":{}|<>]/.test(passwordData.new_password) ? 'mdi-check' : 'mdi-close' }}
                  </v-icon>
                  One special character
                </div>
              </v-card>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="blue-darken-1"
          variant="text"
          @click="closeDialog"
        >
          Cancel
        </v-btn>
        <v-btn
          color="blue-darken-1"
          variant="text"
          @click="changePassword"
          :loading="loading"
          :disabled="!isFormValid"
        >
          Change Password
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue';
import passwordService from '@/services/passwordService';
import { useSnackbar } from '@/composables/useSnackbar';

export default {
  name: 'PasswordChangeDialog',
  
  props: {
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['update:modelValue', 'password-changed'],
  
  setup(props, { emit }) {
    const { showSnackbar } = useSnackbar();
    
    const dialog = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    });
    
    const passwordForm = ref(null);
    const loading = ref(false);
    const policy = ref(null);
    
    const passwordData = ref({
      old_password: '',
      new_password: ''
    });
    
    const confirmPassword = ref('');
    const validationErrors = ref([]);
    
    const passwordRules = computed(() => [
      v => !!v || 'New password is required',
      v => v !== passwordData.value.old_password || 'New password must be different from current password',
      () => validationErrors.value.length === 0 || validationErrors.value.join('; ')
    ]);
    
    const passwordStrength = computed(() => {
      if (!policy.value || !passwordData.value.new_password) {
        return { score: 0, strength: 'Very Weak', color: 'error', feedback: [] };
      }
      
      return passwordService.generatePasswordStrength(passwordData.value.new_password, policy.value);
    });
    
    const isFormValid = computed(() => {
      return passwordData.value.old_password &&
             passwordData.value.new_password &&
             confirmPassword.value === passwordData.value.new_password &&
             validationErrors.value.length === 0;
    });
    
    const loadPasswordPolicy = async () => {
      try {
        const response = await passwordService.getPasswordPolicy();
        policy.value = response.data;
      } catch (error) {
        console.error('Failed to load password policy:', error);
      }
    };
    
    const validateNewPassword = async () => {
      if (!passwordData.value.new_password) {
        validationErrors.value = [];
        return;
      }
      
      try {
        const response = await passwordService.validatePassword(passwordData.value.new_password);
        validationErrors.value = response.data.errors;
      } catch (error) {
        console.error('Failed to validate password:', error);
        validationErrors.value = ['Failed to validate password'];
      }
    };
    
    const changePassword = async () => {
      if (!passwordForm.value.validate()) return;
      
      loading.value = true;
      try {
        const response = await passwordService.changePassword(passwordData.value);
        
        if (response.data.success) {
          showSnackbar('Password changed successfully', 'success');
          emit('password-changed');
          closeDialog();
        } else {
          showSnackbar(response.data.message || 'Failed to change password', 'error');
        }
      } catch (error) {
        console.error('Failed to change password:', error);
        showSnackbar(`Failed to change password: ${error.response?.data?.detail || error.message}`, 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const closeDialog = () => {
      dialog.value = false;
      passwordData.value = { old_password: '', new_password: '' };
      confirmPassword.value = '';
      validationErrors.value = [];
    };
    
    // Watch for dialog opening to load policy
    watch(dialog, (newValue) => {
      if (newValue) {
        loadPasswordPolicy();
      }
    });
    
    onMounted(() => {
      loadPasswordPolicy();
    });
    
    return {
      dialog,
      passwordForm,
      loading,
      policy,
      passwordData,
      confirmPassword,
      passwordRules,
      passwordStrength,
      isFormValid,
      validateNewPassword,
      changePassword,
      closeDialog
    };
  }
};
</script>