<template>
  <div style="padding: 20px; text-align: center;">
    <h1 style="color: #1976D2; margin-bottom: 20px;">🏢 Paksa Financial System</h1>
    <h2 style="color: #333; margin-bottom: 30px;">Welcome to Your Financial Management Platform</h2>
    
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 20px; border-radius: 12px; margin-bottom: 40px;">
      <div style="font-size: 60px; margin-bottom: 20px;">💰</div>
      <h3 style="font-size: 2rem; margin-bottom: 15px;">Comprehensive Financial Management</h3>
      <p style="font-size: 1.2rem; opacity: 0.9;">Everything you need to manage your business finances</p>
    </div>

    <!-- Module Navigation Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 40px;">
      <!-- General Ledger -->
      <div style="background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 20px;">
          <div style="font-size: 2.5rem; margin-bottom: 10px;">📚</div>
          <h4 style="color: #333; margin-bottom: 5px;">General Ledger</h4>
          <p style="color: #666; font-size: 0.9rem;">Complete accounting system</p>
        </div>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
          <button @click="$router.push('/gl/accounts')" style="flex: 1; min-width: 120px; background: #1976D2; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; cursor: pointer;">Chart of Accounts</button>
          <button @click="$router.push('/gl/journal-entries')" style="flex: 1; min-width: 120px; background: #1976D2; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; cursor: pointer;">Journal Entries</button>
        </div>
      </div>
      
      <!-- Accounts Payable -->
      <div style="background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 20px;">
          <div style="font-size: 2.5rem; margin-bottom: 10px;">💳</div>
          <h4 style="color: #333; margin-bottom: 5px;">Accounts Payable</h4>
          <p style="color: #666; font-size: 0.9rem;">Vendor management</p>
        </div>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
          <button @click="$router.push('/ap/vendors')" style="flex: 1; min-width: 120px; background: #F44336; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; cursor: pointer;">Vendors</button>
          <button @click="$router.push('/ap/invoices')" style="flex: 1; min-width: 120px; background: #F44336; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; cursor: pointer;">AP Invoices</button>
        </div>
      </div>
      
      <!-- Accounts Receivable -->
      <div style="background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 20px;">
          <div style="font-size: 2.5rem; margin-bottom: 10px;">💰</div>
          <h4 style="color: #333; margin-bottom: 5px;">Accounts Receivable</h4>
          <p style="color: #666; font-size: 0.9rem;">Customer invoicing</p>
        </div>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
          <button @click="$router.push('/ar/customers')" style="flex: 1; min-width: 120px; background: #4CAF50; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; cursor: pointer;">Customers</button>
          <button @click="$router.push('/ar/invoices')" style="flex: 1; min-width: 120px; background: #4CAF50; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; cursor: pointer;">AR Invoices</button>
        </div>
      </div>
      
      <!-- Payroll -->
      <div style="background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 20px;">
          <div style="font-size: 2.5rem; margin-bottom: 10px;">👥</div>
          <h4 style="color: #333; margin-bottom: 5px;">Payroll</h4>
          <p style="color: #666; font-size: 0.9rem;">Employee management</p>
        </div>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
          <button @click="$router.push('/payroll/employees')" style="flex: 1; min-width: 120px; background: #FF9800; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; cursor: pointer;">Employees</button>
          <button @click="$router.push('/payroll/process')" style="flex: 1; min-width: 120px; background: #FF9800; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; cursor: pointer;">Process Payroll</button>
        </div>
      </div>
      
      <!-- Cash Management -->
      <div style="background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 20px;">
          <div style="font-size: 2.5rem; margin-bottom: 10px;">🏦</div>
          <h4 style="color: #333; margin-bottom: 5px;">Cash Management</h4>
          <p style="color: #666; font-size: 0.9rem;">Banking & reconciliation</p>
        </div>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
          <button @click="$router.push('/cash/accounts')" style="flex: 1; min-width: 120px; background: #00BCD4; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; cursor: pointer;">Bank Accounts</button>
          <button @click="$router.push('/cash/reconciliation')" style="flex: 1; min-width: 120px; background: #00BCD4; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; cursor: pointer;">Reconciliation</button>
        </div>
      </div>
      
      <!-- Fixed Assets -->
      <div style="background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <div style="text-align: center; margin-bottom: 20px;">
          <div style="font-size: 2.5rem; margin-bottom: 10px;">🏭</div>
          <h4 style="color: #333; margin-bottom: 5px;">Fixed Assets</h4>
          <p style="color: #666; font-size: 0.9rem;">Asset management</p>
        </div>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
          <button @click="$router.push('/assets/list')" style="flex: 1; min-width: 120px; background: #9C27B0; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; cursor: pointer;">Asset List</button>
          <button @click="$router.push('/reports')" style="flex: 1; min-width: 120px; background: #9C27B0; color: white; border: none; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; cursor: pointer;">Reports</button>
        </div>
      </div>
    </div>

    <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
      <button 
        @click="$router.push('/dashboard')"
        style="background: #1976D2; color: white; border: none; padding: 15px 30px; border-radius: 8px; font-size: 1.1rem; cursor: pointer; transition: all 0.3s ease;"
        onmouseover="this.style.background='#1565C0'; this.style.transform='translateY(-2px)'"
        onmouseout="this.style.background='#1976D2'; this.style.transform='translateY(0)'"
      >
        📊 Go to Dashboard
      </button>
      
      <button 
        @click="$router.push('/gl/accounts')"
        style="background: transparent; color: #1976D2; border: 2px solid #1976D2; padding: 15px 30px; border-radius: 8px; font-size: 1.1rem; cursor: pointer; transition: all 0.3s ease;"
        onmouseover="this.style.background='#1976D2'; this.style.color='white'"
        onmouseout="this.style.background='transparent'; this.style.color='#1976D2'"
      >
        📋 View Accounts
      </button>
    </div>

    <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
      <h3 style="color: #333; margin-bottom: 20px;">System Status</h3>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px;">
        <div>
          <div style="font-size: 2rem; font-weight: bold; color: #1976D2;">150+</div>
          <div style="color: #666;">Active Accounts</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: bold; color: #4CAF50;">2.5K+</div>
          <div style="color: #666;">Transactions</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: bold; color: #FF9800;">45</div>
          <div style="color: #666;">Employees</div>
        </div>
        <div>
          <div style="font-size: 2rem; font-weight: bold; color: #9C27B0;">500+</div>
          <div style="color: #666;">Reports</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Simple test home page
</script>