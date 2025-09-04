import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const API_BASE_URL = '/api/hrm/email-templates';

interface EmailTemplate {
  id?: string;
  name: string;
  subject: string;
  description: string;
  content: string;
  category: string;
  createdAt?: string;
  updatedAt?: string;
}

export const EmailTemplateService = {
  /**
   * Get all email templates
   */
  async getTemplates(): Promise<{ data: EmailTemplate[] }> {
    try {
      const authStore = useAuthStore();
      const response = await axios.get(API_BASE_URL, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching email templates:', error);
      throw error;
    }
  },

  /**
   * Get a single email template by ID
   */
  async getTemplate(id: string): Promise<{ data: EmailTemplate }> {
    try {
      const authStore = useAuthStore();
      const response = await axios.get(`${API_BASE_URL}/${id}`, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching email template ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create a new email template
   */
  async createTemplate(templateData: Omit<EmailTemplate, 'id'>): Promise<{ data: EmailTemplate }> {
    try {
      const authStore = useAuthStore();
      const response = await axios.post(API_BASE_URL, templateData, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error creating email template:', error);
      throw error;
    }
  },

  /**
   * Update an existing email template
   */
  async updateTemplate(id: string, templateData: Partial<EmailTemplate>): Promise<{ data: EmailTemplate }> {
    try {
      const authStore = useAuthStore();
      const response = await axios.put(`${API_BASE_URL}/${id}`, templateData, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error updating email template ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete an email template
   */
  async deleteTemplate(id: string): Promise<{ success: boolean }> {
    try {
      const authStore = useAuthStore();
      const response = await axios.delete(`${API_BASE_URL}/${id}`, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error deleting email template ${id}:`, error);
      throw error;
    }
  },

  /**
   * Send a test email with the template
   */
  async sendTestEmail(templateId: string, email: string): Promise<{ success: boolean }> {
    try {
      const authStore = useAuthStore();
      const response = await axios.post(
        `${API_BASE_URL}/${templateId}/test`,
        { email },
        {
          headers: {
            'Authorization': `Bearer ${authStore.token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error sending test email:', error);
      throw error;
    }
  },

  /**
   * Get available template variables
   */
  async getTemplateVariables(): Promise<{ data: { [key: string]: string[] } }> {
    try {
      const authStore = useAuthStore();
      const response = await axios.get(`${API_BASE_URL}/variables`, {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching template variables:', error);
      return { data: {} };
    }
  }
};

export default EmailTemplateService;
