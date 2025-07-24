<template>
  <div class="barcode-scanner">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h3>Barcode Scanner</h3>
        <v-btn
          icon
          variant="text"
          @click="$emit('close')"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <!-- Manual Input -->
        <v-text-field
          v-model="barcodeInput"
          label="Scan or Enter Barcode/SKU"
          prepend-inner-icon="mdi-barcode-scan"
          autofocus
          @keyup.enter="lookupItem"
          @input="handleInput"
        >
          <template v-slot:append>
            <v-btn
              color="primary"
              :loading="loading"
              @click="lookupItem"
            >
              Lookup
            </v-btn>
          </template>
        </v-text-field>
        
        <!-- Camera Scanner (if supported) -->
        <div v-if="cameraSupported" class="mt-4">
          <v-btn
            v-if="!showCamera"
            color="secondary"
            prepend-icon="mdi-camera"
            @click="startCamera"
          >
            Use Camera Scanner
          </v-btn>
          
          <div v-else>
            <video
              ref="videoElement"
              class="barcode-video"
              autoplay
              playsinline
            ></video>
            <canvas ref="canvasElement" style="display: none;"></canvas>
            
            <div class="mt-2">
              <v-btn
                color="error"
                prepend-icon="mdi-camera-off"
                @click="stopCamera"
              >
                Stop Camera
              </v-btn>
            </div>
          </div>
        </div>
        
        <!-- Results -->
        <div v-if="foundItem" class="mt-4">
          <v-card variant="outlined" color="success">
            <v-card-title class="text-success">Item Found</v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="6">
                  <div><strong>SKU:</strong> {{ foundItem.sku }}</div>
                  <div><strong>Name:</strong> {{ foundItem.name }}</div>
                  <div v-if="foundItem.barcode"><strong>Barcode:</strong> {{ foundItem.barcode }}</div>
                </v-col>
                <v-col cols="12" md="6">
                  <div><strong>On Hand:</strong> {{ formatQuantity(foundItem.quantity_on_hand) }}</div>
                  <div><strong>Available:</strong> {{ formatQuantity(foundItem.quantity_available) }}</div>
                  <div><strong>Unit Cost:</strong> {{ formatCurrency(foundItem.unit_cost) }}</div>
                </v-col>
              </v-row>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                @click="selectItem"
              >
                Select Item
              </v-btn>
            </v-card-actions>
          </v-card>
        </div>
        
        <div v-if="error" class="mt-4">
          <v-alert type="error" dismissible @click:close="error = ''">
            {{ error }}
          </v-alert>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatCurrency } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';

// Emits
const emit = defineEmits(['close', 'item-selected']);

// Composables
const { showSnackbar } = useSnackbar();

// Refs
const videoElement = ref(null);
const canvasElement = ref(null);

// Data
const barcodeInput = ref('');
const foundItem = ref(null);
const error = ref('');
const loading = ref(false);
const showCamera = ref(false);
const cameraSupported = ref(false);
const stream = ref(null);

// Methods
const handleInput = () => {
  // Clear previous results when typing
  foundItem.value = null;
  error.value = '';
};

const lookupItem = async () => {
  if (!barcodeInput.value.trim()) return;
  
  loading.value = true;
  error.value = '';
  foundItem.value = null;
  
  try {
    const response = await apiClient.get('/api/v1/inventory/barcode/lookup', {
      params: { code: barcodeInput.value.trim() }
    });
    foundItem.value = response.data;
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = 'Item not found. Please check the barcode/SKU and try again.';
    } else {
      error.value = 'Failed to lookup item. Please try again.';
    }
    console.error('Error looking up item:', err);
  } finally {
    loading.value = false;
  }
};

const selectItem = () => {
  if (foundItem.value) {
    emit('item-selected', foundItem.value);
    emit('close');
  }
};

const formatQuantity = (quantity) => {
  return Number(quantity || 0).toLocaleString();
};

// Camera methods
const checkCameraSupport = () => {
  cameraSupported.value = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
};

const startCamera = async () => {
  try {
    stream.value = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' } // Use back camera if available
    });
    
    if (videoElement.value) {
      videoElement.value.srcObject = stream.value;
      showCamera.value = true;
      
      // Start scanning for barcodes (simplified implementation)
      startBarcodeDetection();
    }
  } catch (err) {
    error.value = 'Failed to access camera. Please ensure camera permissions are granted.';
    console.error('Camera error:', err);
  }
};

const stopCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
    stream.value = null;
  }
  showCamera.value = false;
};

const startBarcodeDetection = () => {
  // Simplified barcode detection - in a real implementation,
  // you would use a library like QuaggaJS or ZXing
  const detectBarcode = () => {
    if (!showCamera.value || !videoElement.value) return;
    
    // This is a placeholder for actual barcode detection
    // In practice, you would capture frames and process them
    setTimeout(detectBarcode, 100);
  };
  
  detectBarcode();
};

// Lifecycle hooks
onMounted(() => {
  checkCameraSupport();
});

onUnmounted(() => {
  stopCamera();
});
</script>

<style scoped>
.barcode-scanner {
  max-width: 600px;
  margin: 0 auto;
}

.barcode-video {
  width: 100%;
  max-width: 400px;
  height: 300px;
  border: 2px solid #ccc;
  border-radius: 8px;
}
</style>