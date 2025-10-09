<template>
  <div class="performance-view">
    <div class="grid">
      <div class="col-12">
        <div class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center mb-4 gap-3">
          <div>
            <h1>Performance Management</h1>
            <Breadcrumb :home="home" :model="breadcrumbItems" class="mb-4" />
          </div>
          <div>
            <Button 
              label="New Review" 
              icon="pi pi-plus" 
              class="p-button-success" 
              @click="showNewReviewDialog" 
            />
          </div>
        </div>
      </div>

      <!-- Performance Overview Cards -->
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex justify-content-between align-items-center">
              <div>
                <div class="text-2xl font-bold text-primary">{{ stats.totalReviews }}</div>
                <div class="text-500">Total Reviews</div>
              </div>
              <i class="pi pi-chart-bar text-primary text-3xl"></i>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex justify-content-between align-items-center">
              <div>
                <div class="text-2xl font-bold text-green-500">{{ stats.completedReviews }}</div>
                <div class="text-500">Completed</div>
              </div>
              <i class="pi pi-check-circle text-green-500 text-3xl"></i>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex justify-content-between align-items-center">
              <div>
                <div class="text-2xl font-bold text-orange-500">{{ stats.pendingReviews }}</div>
                <div class="text-500">Pending</div>
              </div>
              <i class="pi pi-clock text-orange-500 text-3xl"></i>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex justify-content-between align-items-center">
              <div>
                <div class="text-2xl font-bold">{{ stats.averageRating }}/5</div>
                <div class="text-500">Avg Rating</div>
              </div>
              <i class="pi pi-star text-yellow-500 text-3xl"></i>
            </div>
          </template>
        </Card>
      </div>

      <!-- Performance Reviews List -->
      <div class="col-12">
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3>Performance Reviews</h3>
              <div class="flex gap-2">
                <InputText 
                  v-model="filters['global'].value" 
                  placeholder="Search reviews..." 
                  class="p-inputtext-sm"
                />
                <Button 
                  icon="pi pi-refresh" 
                  class="p-button-text" 
                  @click="loadReviews" 
                  :loading="loading"
                />
              </div>
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="reviews" 
              :paginator="true" 
              :rows="10"
              :loading="loading"
              :filters="filters"
              :globalFilterFields="['employee_name', 'reviewer_name', 'period', 'status']"
              :rowsPerPageOptions="[5,10,25,50]"
              class="p-datatable-sm"
              responsiveLayout="scroll"
            >
              <template #empty>No performance reviews found.</template>
              <Column field="employee_name" header="Employee" :sortable="true">
                <template #body="{ data }">
                  <div class="flex align-items-center">
                    <Avatar :label="data.employee_name.charAt(0)" class="mr-2" />
                    <span class="font-medium">{{ data.employee_name }}</span>
                  </div>
                </template>
              </Column>
              <Column field="reviewer_name" header="Reviewer" :sortable="true" />
              <Column field="period" header="Review Period" :sortable="true" />
              <Column field="overall_rating" header="Rating" :sortable="true">
                <template #body="{ data }">
                  <div class="flex align-items-center">
                    <Rating :modelValue="data.overall_rating" :readonly="true" :cancel="false" />
                    <span class="ml-2">{{ data.overall_rating }}/5</span>
                  </div>
                </template>
              </Column>
              <Column field="status" header="Status" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column field="review_date" header="Review Date" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.review_date) }}
                </template>
              </Column>
              <Column header="Actions" style="min-width: 10rem">
                <template #body="{ data }">
                  <div class="flex gap-2">
                    <Button 
                      icon="pi pi-eye" 
                      class="p-button-text p-button-sm" 
                      @click="viewReview(data)" 
                      v-tooltip.top="'View Review'"
                    />
                    <Button 
                      icon="pi pi-pencil" 
                      class="p-button-text p-button-sm p-button-warning" 
                      @click="editReview(data)" 
                      v-tooltip.top="'Edit Review'"
                    />
                    <Button 
                      icon="pi pi-trash" 
                      class="p-button-text p-button-sm p-button-danger" 
                      @click="confirmDeleteReview(data)" 
                      v-tooltip.top="'Delete Review'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- New Review Dialog -->
    <Dialog 
      v-model:visible="reviewDialog" 
      :style="{width: '800px', maxWidth: '95vw'}" 
      :header="editing ? 'Edit Performance Review' : 'New Performance Review'" 
      :modal="true"
      :closable="!submitting"
      class="p-fluid"
    >
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="employee">Employee <span class="text-red-500">*</span></label>
            <Dropdown 
              id="employee" 
              v-model="review.employee_id" 
              :options="employees" 
              optionLabel="name" 
              optionValue="id" 
              placeholder="Select employee"
              :class="{'p-invalid': submitted && !review.employee_id}"
              filter
            />
            <small class="p-error" v-if="submitted && !review.employee_id">Employee is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="reviewer">Reviewer <span class="text-red-500">*</span></label>
            <Dropdown 
              id="reviewer" 
              v-model="review.reviewer_id" 
              :options="employees" 
              optionLabel="name" 
              optionValue="id" 
              placeholder="Select reviewer"
              :class="{'p-invalid': submitted && !review.reviewer_id}"
              filter
            />
            <small class="p-error" v-if="submitted && !review.reviewer_id">Reviewer is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="period">Review Period</label>
            <InputText 
              id="period" 
              v-model="review.period" 
              placeholder="e.g., Q1 2024, Annual 2024"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="review_date">Review Date</label>
            <Calendar 
              id="review_date" 
              v-model="review.review_date" 
              dateFormat="yy-mm-dd" 
              :showIcon="true"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="overall_rating">Overall Rating</label>
            <Rating v-model="review.overall_rating" :cancel="false" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="strengths">Strengths</label>
            <Textarea id="strengths" v-model="review.strengths" rows="3" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="areas_for_improvement">Areas for Improvement</label>
            <Textarea id="areas_for_improvement" v-model="review.areas_for_improvement" rows="3" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="goals">Goals for Next Period</label>
            <Textarea id="goals" v-model="review.goals" rows="3" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="status">Status</label>
            <Dropdown 
              id="status" 
              v-model="review.status" 
              :options="statuses" 
              optionLabel="label" 
              optionValue="value"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="hideDialog" 
          :disabled="submitting"
        />
        <Button 
          :label="editing ? 'Update' : 'Save'" 
          icon="pi pi-check" 
          class="p-button-text" 
          @click="saveReview" 
          :loading="submitting"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deleteReviewDialog" 
      :style="{width: '450px'}" 
      header="Confirm" 
      :modal="true"
    >
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="review">Are you sure you want to delete this performance review?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="deleteReviewDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="deleteReview"
          :loading="deleting"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'primevue/usetoast';
import { hrmService } from '@/services/hrmService';

const toast = useToast();

// Data
const reviews = ref([]);
const employees = ref([]);
const review = ref({
  id: null,
  employee_id: null,
  reviewer_id: null,
  review_period_start: new Date().toISOString().split('T')[0],
  review_period_end: new Date().toISOString().split('T')[0],
  review_date: new Date().toISOString().split('T')[0],
  overall_rating: 3,
  overall_rating_text: 'MEETS_EXPECTATIONS',
  strengths: '',
  areas_for_improvement: '',
  goals: '',
  manager_comments: '',
  status: 'DRAFT'
});

// Stats
const stats = ref({
  totalReviews: 0,
  completedReviews: 0,
  pendingReviews: 0,
  averageRating: 0
});

// UI State
const loading = ref(false);
const submitting = ref(false);
const deleting = ref(false);
const reviewDialog = ref(false);
const deleteReviewDialog = ref(false);
const editing = ref(false);
const submitted = ref(false);

// Filters
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS }
});

// Options
const statuses = ref([
  { label: 'Draft', value: 'draft' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
  { label: 'Approved', value: 'approved' }
]);

// Breadcrumb
const home = ref({ icon: 'pi pi-home', to: '/' });
const breadcrumbItems = ref([
  { label: 'HRM', to: '/hrm' },
  { label: 'Performance' }
]);

// Methods
const loadReviews = async () => {
  loading.value = true;
  try {
    const response = await hrmService.getPerformanceReviews();
    const reviewsData = response.data || [];
    
    // Transform data for display
    reviews.value = reviewsData.map(review => ({
      id: review.id,
      employee_name: review.employee?.full_name || `${review.employee?.first_name} ${review.employee?.last_name}`,
      reviewer_name: review.reviewer?.full_name || `${review.reviewer?.first_name} ${review.reviewer?.last_name}`,
      period: `${review.review_period_start} to ${review.review_period_end}`,
      overall_rating: getRatingNumber(review.overall_rating),
      status: review.status.toLowerCase(),
      review_date: review.review_date
    }));

    // Update stats
    stats.value = {
      totalReviews: reviews.value.length,
      completedReviews: reviews.value.filter(r => r.status === 'completed' || r.status === 'approved').length,
      pendingReviews: reviews.value.filter(r => r.status === 'draft' || r.status === 'in_progress').length,
      averageRating: reviews.value.reduce((sum, r) => sum + r.overall_rating, 0) / reviews.value.length || 0
    };
    stats.value.averageRating = Math.round(stats.value.averageRating * 10) / 10;

  } catch (error) {
    console.error('Error loading reviews:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load performance reviews',
      life: 3000
    });
    
    // Fallback to empty data
    reviews.value = [];
    stats.value = {
      totalReviews: 0,
      completedReviews: 0,
      pendingReviews: 0,
      averageRating: 0
    };
  } finally {
    loading.value = false;
  }
};

const loadEmployees = async () => {
  try {
    const response = await hrmService.getEmployees({ is_active: true });
    employees.value = (response.data || []).map(emp => ({
      id: emp.id!,
      name: emp.full_name || `${emp.first_name} ${emp.last_name}`
    }));
  } catch (error) {
    console.error('Error loading employees:', error);
    // Fallback to empty array
    employees.value = [];
  }
};

const getRatingNumber = (rating: string): number => {
  const ratingMap: { [key: string]: number } = {
    'OUTSTANDING': 5,
    'EXCEEDS_EXPECTATIONS': 4,
    'MEETS_EXPECTATIONS': 3,
    'BELOW_EXPECTATIONS': 2,
    'UNSATISFACTORY': 1
  };
  return ratingMap[rating] || 3;
};

const showNewReviewDialog = () => {
  review.value = {
    id: null,
    employee_id: null,
    reviewer_id: null,
    period: '',
    review_date: new Date(),
    overall_rating: 3,
    strengths: '',
    areas_for_improvement: '',
    goals: '',
    status: 'draft'
  };
  editing.value = false;
  submitted.value = false;
  reviewDialog.value = true;
};

const editReview = (data: any) => {
  review.value = { ...data };
  editing.value = true;
  submitted.value = false;
  reviewDialog.value = true;
};

const viewReview = (data: any) => {
  // Navigate to detailed review view or show in modal
  toast.add({
    severity: 'info',
    summary: 'Info',
    detail: `Viewing review for ${data.employee_name}`,
    life: 3000
  });
};

const hideDialog = () => {
  reviewDialog.value = false;
  submitted.value = false;
};

const saveReview = async () => {
  submitted.value = true;
  
  if (!review.value.employee_id || !review.value.reviewer_id) {
    return;
  }

  submitting.value = true;
  try {
    const reviewData = {
      review_period_start: review.value.review_period_start,
      review_period_end: review.value.review_period_end,
      review_date: review.value.review_date,
      overall_rating: review.value.overall_rating_text || 'MEETS_EXPECTATIONS',
      strengths: review.value.strengths,
      areas_for_improvement: review.value.areas_for_improvement,
      development_goals: review.value.goals,
      manager_comments: review.value.manager_comments
    };
    
    if (editing.value && review.value.id) {
      await hrmService.updatePerformanceReview(review.value.id, reviewData);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Review updated successfully',
        life: 3000
      });
    } else {
      await hrmService.createPerformanceReview(
        review.value.employee_id,
        review.value.reviewer_id,
        reviewData
      );
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Review created successfully',
        life: 3000
      });
    }
    
    hideDialog();
    await loadReviews();
  } catch (error) {
    console.error('Error saving review:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save review',
      life: 3000
    });
  } finally {
    submitting.value = false;
  }
};

const confirmDeleteReview = (data: any) => {
  review.value = data;
  deleteReviewDialog.value = true;
};

const deleteReview = async () => {
  if (!review.value.id) return;
  
  deleting.value = true;
  try {
    await hrmService.deletePerformanceReview(review.value.id);
    
    deleteReviewDialog.value = false;
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Review deleted successfully',
      life: 3000
    });
    await loadReviews();
  } catch (error) {
    console.error('Error deleting review:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete review',
      life: 3000
    });
  } finally {
    deleting.value = false;
  }
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString();
};

const getStatusSeverity = (status: string) => {
  const severityMap: { [key: string]: string } = {
    draft: 'secondary',
    in_progress: 'warning',
    completed: 'success',
    approved: 'info'
  };
  return severityMap[status] || 'secondary';
};

// Lifecycle
onMounted(() => {
  loadReviews();
  loadEmployees();
});
</script>

<style scoped>
.performance-view {
  padding: 1rem;
}
</style>