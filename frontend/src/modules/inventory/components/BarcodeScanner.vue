<template>
  <div class="barcode-scanner">
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <h3 class="m-0">Barcode Scanner</h3>
          <Button icon="pi pi-times" text @click="$emit('close')" />
        </div>
      </template>
      
      <template #content>
        <!-- Manual Input -->
        <div class="field">
          <label class="font-semibold">Scan or Enter Barcode/SKU</label>
          <div class="p-inputgroup">
            <span class="p-inputgroup-addon">
              <i class="pi pi-qrcode"></i>
            </span>
            <InputText
              v-model="barcodeInput"
              placeholder="Enter barcode or SKU"
              autofocus
              @keyup.enter="lookupItem"
              @input="handleInput"
            />
            <Button
              label="Lookup"
              :loading="loading"
              @click="lookupItem"
            />
          </div>
        </div>
        
        <!-- Camera Scanner (if supported) -->
        <div v-if="cameraSupported" class="mt-4">
          <Button
            v-if="!showCamera"
            icon="pi pi-camera"
            label="Use Camera Scanner"
            severity="secondary"
            @click="startCamera"
          />
          
          <div v-else>
            <video
              ref="videoElement"
              class="barcode-video"
              autoplay
              playsinline
            ></video>
            <canvas ref="canvasElement" style="display: none;"></canvas>
            
            <div class="mt-2">
              <Button
                icon="pi pi-camera"
                label="Stop Camera"
                severity="danger"
                @click="stopCamera"
              />
            </div>
          </div>
        </div>
        
        <!-- Results -->
        <div v-if="foundItem" class="mt-4">
          <Card class="border-green-500">
            <template #title>
              <span class="text-green-600">Item Found</span>
            </template>
            <template #content>
              <div class="grid">
                <div class="col-12 md:col-6">
                  <div><strong>SKU:</strong> {{ foundItem.sku }}</div>
                  <div><strong>Name:</strong> {{ foundItem.name }}</div>
                  <div v-if="foundItem.barcode"><strong>Barcode:</strong> {{ foundItem.barcode }}</div>
                </div>
                <div class="col-12 md:col-6">
                  <div><strong>On Hand:</strong> {{ formatQuantity(foundItem.quantity_on_hand) }}</div>
                  <div><strong>Available:</strong> {{ formatQuantity(foundItem.quantity_available) }}</div>
                  <div><strong>Unit Cost:</strong> {{ formatCurrency(foundItem.unit_cost) }}</div>
                </div>
              </div>
              <div class="flex justify-content-end mt-3">
                <Button
                  label="Select Item"
                  @click="selectItem"
                />
              </div>
            </template>
          </Card>
        </div>
        
        <div v-if="error" class="mt-4">
          <Message severity="error" :closable="true" @close="error = ''">
            {{ error }}
          </Message>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { inventoryService } from '@/services/inventoryService'

// Emits
const emit = defineEmits(['close', 'item-selected']);

// Composables
const toast = useToast()

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
    const item = await inventoryService.lookupByBarcode(barcodeInput.value.trim());
    foundItem.value = {
      sku: item.item_code,
      name: item.item_name,
      barcode: item.barcode,
      quantity_on_hand: item.quantity_on_hand || 0,
      quantity_available: item.quantity_on_hand || 0,
      unit_cost: item.cost_price || 0
    };
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = 'Item not found. Please check the barcode/SKU and try again.'
    } else {
      error.value = 'Failed to lookup item. Please try again.'
    }
    console.error('Error looking up item:', err)
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
    error.value = 'Failed to access camera. Please ensure camera permissions are granted.'
    console.error('Camera error:', err)
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