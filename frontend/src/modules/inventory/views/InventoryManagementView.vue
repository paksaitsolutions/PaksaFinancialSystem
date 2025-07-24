<template>
  <div class="inventory-management">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-4">Inventory Management</h1>
          
          <v-card v-if="selectedItem">
            <v-card-text class="pa-0">
              <div class="d-flex align-center px-4 py-2 bg-grey-lighten-4">
                <v-btn
                  variant="text"
                  prepend-icon="mdi-arrow-left"
                  @click="clearSelection"
                >
                  Back to List
                </v-btn>
                <v-spacer></v-spacer>
                <div class="text-h6">{{ selectedItem.name }} ({{ selectedItem.sku }})</div>
              </div>
              
              <!-- Item detail view would go here -->
              <div class="pa-4">
                <p>Inventory item detail view will be implemented here.</p>
              </div>
            </v-card-text>
          </v-card>
          
          <v-card v-else-if="isCreating">
            <v-card-text class="pa-0">
              <div class="d-flex align-center px-4 py-2 bg-grey-lighten-4">
                <v-btn
                  variant="text"
                  prepend-icon="mdi-arrow-left"
                  @click="clearSelection"
                >
                  Back to List
                </v-btn>
                <v-spacer></v-spacer>
                <div class="text-h6">Add New Inventory Item</div>
              </div>
              
              <!-- Item creation form would go here -->
              <div class="pa-4">
                <p>Inventory item creation form will be implemented here.</p>
              </div>
            </v-card-text>
          </v-card>
          
          <div v-else>
            <v-tabs v-model="activeTab" bg-color="primary">
              <v-tab value="items">Items</v-tab>
              <v-tab value="reports">Reports & Analytics</v-tab>
              <v-tab value="forecast">Forecasting</v-tab>
              <v-tab value="purchase-orders">Purchase Orders</v-tab>
              <v-tab value="cycle-counts">Cycle Counting</v-tab>
              <v-tab value="adjustments">Stock Adjustments</v-tab>
              <v-tab value="categories">Categories</v-tab>
              <v-tab value="locations">Locations</v-tab>
              <v-tab value="transactions">Transactions</v-tab>
            </v-tabs>
            
            <v-window v-model="activeTab" class="mt-4">
              <v-window-item value="items">
                <inventory-list
                  @view="viewItem"
                  @create="createItem"
                />
              </v-window-item>
              
              <v-window-item value="reports">
                <inventory-reports />
              </v-window-item>
              
              <v-window-item value="forecast">
                <inventory-forecast />
              </v-window-item>
              
              <v-window-item value="purchase-orders">
                <v-card>
                  <v-card-title class="d-flex align-center justify-space-between">
                    <h3>Purchase Orders</h3>
                    <v-btn color="primary" prepend-icon="mdi-plus" @click="showPurchaseOrderForm = true">
                      New Purchase Order
                    </v-btn>
                  </v-card-title>
                  <v-card-text>
                    <purchase-order-form
                      v-if="showPurchaseOrderForm"
                      @saved="handlePurchaseOrderSaved"
                      @cancelled="showPurchaseOrderForm = false"
                    />
                    <div v-else>
                      <p>Purchase order list will be displayed here.</p>
                    </div>
                  </v-card-text>
                </v-card>
              </v-window-item>
              
              <v-window-item value="cycle-counts">
                <v-card>
                  <v-card-title class="d-flex align-center justify-space-between">
                    <h3>Cycle Counting</h3>
                    <v-btn color="primary" prepend-icon="mdi-plus" @click="showCycleCountForm = true">
                      New Cycle Count
                    </v-btn>
                  </v-card-title>
                  <v-card-text>
                    <cycle-count-form
                      v-if="showCycleCountForm"
                      @saved="handleCycleCountSaved"
                      @cancelled="showCycleCountForm = false"
                    />
                    <div v-else>
                      <p>Cycle count list will be displayed here.</p>
                    </div>
                  </v-card-text>
                </v-card>
              </v-window-item>
              
              <v-window-item value="adjustments">
                <v-card>
                  <v-card-title class="d-flex align-center justify-space-between">
                    <h3>Stock Adjustments</h3>
                    <v-btn color="primary" prepend-icon="mdi-plus" @click="showAdjustmentForm = true">
                      New Adjustment
                    </v-btn>
                  </v-card-title>
                  <v-card-text>
                    <stock-adjustment-form
                      v-if="showAdjustmentForm"
                      @saved="handleAdjustmentSaved"
                      @cancelled="showAdjustmentForm = false"
                    />
                    <div v-else>
                      <p>Stock adjustment history will be displayed here.</p>
                    </div>
                  </v-card-text>
                </v-card>
              </v-window-item>
              
              <v-window-item value="categories">
                <category-management />
              </v-window-item>
              
              <v-window-item value="locations">
                <location-management />
              </v-window-item>
              
              <v-window-item value="transactions">
                <transaction-history />
              </v-window-item>
            </v-window>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import InventoryList from '../components/InventoryList.vue';
import StockAdjustmentForm from '../components/StockAdjustmentForm.vue';
import CategoryManagement from '../components/CategoryManagement.vue';
import PurchaseOrderForm from '../components/PurchaseOrderForm.vue';
import InventoryReports from '../components/InventoryReports.vue';
import CycleCountForm from '../components/CycleCountForm.vue';
import InventoryForecast from '../components/InventoryForecast.vue';
import LocationManagement from '../components/LocationManagement.vue';
import TransactionHistory from '../components/TransactionHistory.vue';

// Data
const activeTab = ref('items');
const selectedItem = ref(null);
const isCreating = ref(false);
const showAdjustmentForm = ref(false);
const showPurchaseOrderForm = ref(false);
const showCycleCountForm = ref(false);

// Methods
const viewItem = (item) => {
  selectedItem.value = item;
  isCreating.value = false;
};

const createItem = () => {
  selectedItem.value = null;
  isCreating.value = true;
};

const clearSelection = () => {
  selectedItem.value = null;
  isCreating.value = false;
};

const handleAdjustmentSaved = () => {
  showAdjustmentForm.value = false;
};

const handlePurchaseOrderSaved = () => {
  showPurchaseOrderForm.value = false;
};

const handleCycleCountSaved = () => {
  showCycleCountForm.value = false;
};
</script>

<style scoped>
.inventory-management {
  padding: 16px;
}
</style>