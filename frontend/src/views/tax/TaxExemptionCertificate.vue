<template>
  <div class="tax-exemption-certificate">
    <div class="certificate-header">
      <h1>Tax Exemption Certificate</h1>
      <div class="certificate-actions">
        <button @click="printCertificate" class="print-button">
          <i class="fas fa-print"></i> Print Certificate
        </button>
        <button @click="downloadPDF" class="download-button">
          <i class="fas fa-download"></i> Download PDF
        </button>
      </div>
    </div>

    <div class="certificate-content">
      <div class="company-info">
        <h2>Company Information</h2>
        <div class="info-grid">
          <div>
            <strong>Company Name:</strong>
            <span>{{ company.name }}</span>
          </div>
          <div>
            <strong>Tax ID:</strong>
            <span>{{ company.taxId }}</span>
          </div>
          <div>
            <strong>Registration Date:</strong>
            <span>{{ formatDate(company.registrationDate) }}</span>
          </div>
        </div>
      </div>

      <div class="exemption-details">
        <h2>Exemption Details</h2>
        <div class="details-grid">
          <div>
            <strong>Exemption Type:</strong>
            <span>{{ exemption.type }}</span>
          </div>
          <div>
            <strong>Effective Date:</strong>
            <span>{{ formatDate(exemption.effectiveDate) }}</span>
          </div>
          <div>
            <strong>Expiry Date:</strong>
            <span>{{ formatDate(exemption.expiryDate) }}</span>
          </div>
          <div>
            <strong>Reason:</strong>
            <span>{{ exemption.reason }}</span>
          </div>
        </div>
      </div>

      <div class="terms-conditions">
        <h2>Terms and Conditions</h2>
        <ul>
          <li v-for="(condition, index) in exemption.terms" :key="index">
            {{ condition }}
          </li>
        </ul>
      </div>

      <div class="signature-section">
        <div class="signature-box">
          <div class="signature-line">
            <span>_________________________</span>
          </div>
          <div class="signature-text">
            <span>Authorized Signatory</span>
          </div>
        </div>
        <div class="date-box">
          <div class="date-text">
            <span>Date: {{ formatDate(new Date()) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useCompanyStore } from '@/stores/company';
import { useTaxPolicyStore } from '@/stores/tax/policy';
import { formatDate } from '@/utils/date';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';

const companyStore = useCompanyStore();
const taxPolicyStore = useTaxPolicyStore();
const company = ref({ name: '', taxId: '', registrationDate: '' });
const exemption = ref({
  type: '',
  effectiveDate: '',
  expiryDate: '',
  reason: '',
  terms: []
});

onMounted(async () => {
  await fetchCompanyInfo();
  await fetchExemptionDetails();
});

async function fetchCompanyInfo() {
  try {
    company.value = await companyStore.getCompanyProfile();
  } catch (error) {
    console.error('Error fetching company info:', error);
  }
}

async function fetchExemptionDetails() {
  try {
    const currentExemption = await taxPolicyStore.getTaxExemptions();
    if (currentExemption.length > 0) {
      exemption.value = currentExemption[0];
    }
  } catch (error) {
    console.error('Error fetching exemption details:', error);
  }
}

function printCertificate() {
  window.print();
}

function downloadPDF() {
  html2canvas(document.querySelector('.certificate-content')).then(canvas => {
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF();
    pdf.addImage(imgData, 'PNG', 15, 40, 180, 0);
    pdf.save('tax-exemption-certificate.pdf');
  });
}
</script>

<style scoped>
.tax-exemption-certificate {
  max-width: 800px;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.certificate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.certificate-actions {
  display: flex;
  gap: 1rem;
}

button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.print-button {
  background: #4CAF50;
  color: white;
}

.download-button {
  background: #2196F3;
  color: white;
}

.certificate-content {
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

h1, h2 {
  color: #333;
  margin: 1rem 0;
}

.info-grid, .details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.info-grid div, .details-grid div {
  display: flex;
  flex-direction: column;
}

strong {
  color: #666;
  margin-bottom: 0.25rem;
}

span {
  color: #333;
}

.terms-conditions {
  margin-top: 2rem;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  margin-bottom: 0.5rem;
}

.signature-section {
  margin-top: 3rem;
  display: flex;
  justify-content: space-between;
  border-top: 2px solid #ddd;
  padding-top: 2rem;
}

.signature-box, .date-box {
  width: 45%;
}

.signature-line {
  border-top: 2px solid #666;
  margin-bottom: 1rem;
}

.signature-text, .date-text {
  text-align: center;
  font-size: 0.9rem;
  color: #666;
}
</style>
