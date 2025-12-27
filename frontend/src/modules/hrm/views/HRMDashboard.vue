<template>
  <div class="hrm-dashboard">
    <div class="page-header">
      <h1>Human Resources Dashboard</h1>
      <p class="subtitle">Employee management and HR analytics</p>
    </div>

    <div class="dashboard-grid">
      <!-- KPI Cards -->
      <div class="kpi-section">
        <div class="kpi-card">
          <div class="kpi-icon">
            <i class="pi pi-users"></i>
          </div>
          <div class="kpi-content">
            <h3>Total Employees</h3>
            <div class="kpi-value">{{ totalEmployees }}</div>
            <div class="kpi-change positive">+5 this month</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon">
            <i class="pi pi-calendar"></i>
          </div>
          <div class="kpi-content">
            <h3>Active Leave Requests</h3>
            <div class="kpi-value">{{ activeLeaveRequests }}</div>
            <div class="kpi-change">{{ pendingApprovals }} pending</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon">
            <i class="pi pi-chart-line"></i>
          </div>
          <div class="kpi-content">
            <h3>Attendance Rate</h3>
            <div class="kpi-value">{{ attendanceRate }}%</div>
            <div class="kpi-change positive">+2.1% vs last month</div>
          </div>
        </div>

        <div class="kpi-card">
          <div class="kpi-icon">
            <i class="pi pi-star"></i>
          </div>
          <div class="kpi-content">
            <h3>Performance Score</h3>
            <div class="kpi-value">{{ performanceScore }}</div>
            <div class="kpi-change positive">+0.3 improvement</div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <Card class="quick-actions">
        <template #title>Quick Actions</template>
        <template #content>
          <div class="action-buttons">
            <Button label="Add Employee" icon="pi pi-plus" class="p-button-outlined" />
            <Button label="Process Leave" icon="pi pi-calendar" class="p-button-outlined" />
            <Button label="View Reports" icon="pi pi-chart-bar" class="p-button-outlined" />
            <Button label="Performance Review" icon="pi pi-star" class="p-button-outlined" />
          </div>
        </template>
      </Card>

      <!-- Recent Activity -->
      <Card class="recent-activity">
        <template #title>Recent Activity</template>
        <template #content>
          <div class="activity-list">
            <div class="activity-item" v-for="activity in recentActivities" :key="activity.id">
              <div class="activity-icon">
                <i :class="activity.icon"></i>
              </div>
              <div class="activity-content">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-time">{{ activity.time }}</div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const totalEmployees = ref(156)
const activeLeaveRequests = ref(12)
const pendingApprovals = ref(5)
const attendanceRate = ref(94.2)
const performanceScore = ref(4.2)

const recentActivities = ref([
  {
    id: 1,
    title: 'New employee onboarded - John Smith',
    time: '2 hours ago',
    icon: 'pi pi-user-plus'
  },
  {
    id: 2,
    title: 'Leave request approved - Sarah Johnson',
    time: '4 hours ago',
    icon: 'pi pi-check'
  },
  {
    id: 3,
    title: 'Performance review completed - Mike Davis',
    time: '1 day ago',
    icon: 'pi pi-star'
  },
  {
    id: 4,
    title: 'Training session scheduled',
    time: '2 days ago',
    icon: 'pi pi-calendar'
  }
])

onMounted(() => {
  // Load dashboard data
})
</script>

<style scoped>
.hrm-dashboard {
  padding: 1.5rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.subtitle {
  margin: 0;
  color: #6c757d;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 1.5rem;
}

.kpi-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.kpi-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.kpi-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #e3f2fd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1976d2;
  font-size: 1.5rem;
}

.kpi-content h3 {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

.kpi-value {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.kpi-change {
  font-size: 0.75rem;
  color: #6c757d;
}

.kpi-change.positive {
  color: #28a745;
}

.quick-actions,
.recent-activity {
  height: fit-content;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 6px;
  background: #f8f9fa;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e3f2fd;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1976d2;
  font-size: 0.875rem;
}

.activity-title {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.activity-time {
  font-size: 0.75rem;
  color: #6c757d;
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .kpi-section {
    grid-template-columns: 1fr;
  }
}
</style>