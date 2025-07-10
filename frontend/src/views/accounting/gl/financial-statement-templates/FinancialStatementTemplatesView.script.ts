import { defineComponent, ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useRouter } from 'vue-router';
import { format } from 'date-fns';
import financialStatementService from '@/services/financialStatementService';
import type { 
  FinancialStatementTemplate, 
  FinancialStatementLine,
  FinancialStatementType,
  LineType
} from '@/types/financial';

export default defineComponent({
  name: 'FinancialStatementTemplatesView',
  
  setup() {
    const toast = useToast();
    const confirm = useConfirm();
    const router = useRouter();
    
    // State
    const templates = ref<FinancialStatementTemplate[]>([]);
    const loading = ref(false);
    const saving = ref(false);
    const deleting = ref(false);
    const submitted = ref(false);
    const showTemplateDialog = ref(false);
    const editingTemplate = ref<FinancialStatementTemplate | null>(null);
    const expandedKeys = ref<Record<string, boolean>>({});
    const accounts = ref<any[]>([]);
    const filteredAccounts = ref<any[]>([]);
    
    // Pagination
    const totalRecords = ref(0);
    const page = ref(1);
    const limit = ref(10);
    const sortField = ref('name');
    const sortOrder = ref(1); // 1 for asc, -1 for desc
    const filters = ref<any>({});
    
    // Dialogs
    const deleteDialog = ref({
      visible: false,
      template: null as FinancialStatementTemplate | null
    });
    
    const previewDialog = ref({
      visible: false,
      template: null as FinancialStatementTemplate | null
    });
    
    // Form
    const templateForm = ref<Partial<FinancialStatementTemplate>>({
      name: '',
      description: '',
      statement_type: undefined,
      is_default: false,
      structure: []
    });
    
    // Computed
    const showAccountNumberColumn = computed(() => {
      return templateForm.value.structure?.some((line: FinancialStatementLine) => 
        line.line_type === 'account'
      );
    });
    
    const showFormulaColumn = computed(() => {
      return templateForm.value.structure?.some((line: FinancialStatementLine) => 
        line.line_type === 'calculation'
      );
    });
    
    const statementTypeOptions = [
      { label: 'Balance Sheet', value: 'balance_sheet' },
      { label: 'Income Statement', value: 'income_statement' },
      { label: 'Cash Flow', value: 'cash_flow' },
      { label: 'Custom', value: 'custom' }
    ];
    
    // Methods
    const loadTemplates = async () => {
      try {
        loading.value = true;
        const response = await financialStatementService.getTemplates();
        templates.value = response;
        totalRecords.value = response.length; // Update with actual total from API if paginated
      } catch (error) {
        console.error('Error loading templates:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load financial statement templates',
          life: 5000
        });
      } finally {
        loading.value = false;
      }
    };
    
    const onPage = (event: any) => {
      page.value = event.page + 1;
      loadTemplates();
    };
    
    const onSort = (event: any) => {
      sortField.value = event.sortField;
      sortOrder.value = event.sortOrder;
      loadTemplates();
    };
    
    const formatDate = (dateString: string) => {
      if (!dateString) return '-';
      return format(new Date(dateString), 'MMM d, yyyy h:mm a');
    };
    
    const formatStatementType = (type: string) => {
      const option = statementTypeOptions.find(opt => opt.value === type);
      return option ? option.label : type;
    };
    
    const getLineStyle = (node: any) => {
      return {
        'font-bold': node.data.line_type === 'header' || node.data.line_type === 'total',
        'font-italic': node.data.is_italic,
        'underline': node.data.is_underline,
        'ml-2': node.level > 0,
        'ml-4': node.level > 1,
        'ml-6': node.level > 2,
      };
    };
    
    const editTemplate = (template: FinancialStatementTemplate) => {
      editingTemplate.value = { ...template };
      templateForm.value = {
        ...template,
        structure: JSON.parse(JSON.stringify(template.structure)) // Deep clone
      };
      showTemplateDialog.value = true;
      
      // Expand all nodes
      const keys: Record<string, boolean> = {};
      const expandNodes = (nodes: any[], level = 0) => {
        nodes.forEach((node, index) => {
          const nodeKey = `${level}_${index}`;
          keys[nodeKey] = true;
          if (node.children && node.children.length > 0) {
            expandNodes(node.children, level + 1);
          }
        });
      };
      
      expandNodes(templateForm.value.structure || []);
      expandedKeys.value = keys;
    };
    
    const previewTemplate = (template: FinancialStatementTemplate) => {
      previewDialog.value = {
        visible: true,
        template: { ...template }
      };
    };
    
    const cloneTemplate = (template: FinancialStatementTemplate) => {
      editingTemplate.value = null;
      templateForm.value = {
        ...template,
        id: undefined,
        name: `${template.name} (Copy)`,
        is_default: false,
        structure: JSON.parse(JSON.stringify(template.structure)) // Deep clone
      };
      showTemplateDialog.value = true;
    };
    
    const confirmDeleteTemplate = (template: FinancialStatementTemplate) => {
      deleteDialog.value = {
        visible: true,
        template
      };
    };
    
    const deleteTemplate = async () => {
      if (!deleteDialog.value.template) return;
      
      try {
        deleting.value = true;
        await financialStatementService.deleteTemplate(deleteDialog.value.template.id);
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Template deleted successfully',
          life: 3000
        });
        
        // Reload templates
        await loadTemplates();
      } catch (error) {
        console.error('Error deleting template:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete template',
          life: 5000
        });
      } finally {
        deleteDialog.value.visible = false;
        deleting.value = false;
      }
    };
    
    const addLine = (type: LineType, parentId?: string) => {
      if (!templateForm.value.structure) {
        templateForm.value.structure = [];
      }
      
      const newLine: FinancialStatementLine = {
        id: `new-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
        code: '',
        name: '',
        line_type: type,
        level: 0,
        display_order: templateForm.value.structure.length,
        is_bold: type === 'header' || type === 'total',
        is_italic: false,
        is_underline: false,
        show_currency_symbol: true,
        show_thousands_separator: true,
        decimal_places: 2,
        parent_id: parentId
      };
      
      switch (type) {
        case 'header':
          newLine.name = 'New Header';
          break;
        case 'account':
          newLine.name = 'Account Line';
          break;
        case 'calculation':
          newLine.name = 'Calculation';
          newLine.calculation_formula = '';
          break;
        case 'total':
          newLine.name = 'Total';
          break;
        case 'subtotal':
          newLine.name = 'Subtotal';
          break;
      }
      
      if (parentId) {
        // Add as child
        const parent = findNodeById(templateForm.value.structure, parentId);
        if (parent) {
          if (!parent.children) {
            parent.children = [];
          }
          newLine.level = (parent.level || 0) + 1;
          newLine.display_order = parent.children.length;
          parent.children.push(newLine);
          
          // Expand parent
          const parentKey = Object.keys(expandedKeys.value).find(key => 
            key.endsWith(`_${parent.display_order}`)
          );
          if (parentKey) {
            expandedKeys.value[parentKey] = true;
          }
        }
      } else {
        // Add to root
        newLine.display_order = templateForm.value.structure.length;
        templateForm.value.structure.push(newLine);
      }
      
      // Trigger reactivity
      templateForm.value.structure = [...templateForm.value.structure];
    };
    
    const addChildLine = (node: any) => {
      addLine('account', node.data.id);
    };
    
    const removeLine = (node: any) => {
      if (!templateForm.value.structure) return;
      
      const removeNode = (nodes: any[], id: string): boolean => {
        for (let i = 0; i < nodes.length; i++) {
          if (nodes[i].id === id) {
            nodes.splice(i, 1);
            return true;
          }
          
          if (nodes[i].children && nodes[i].children.length > 0) {
            if (removeNode(nodes[i].children, id)) {
              return true;
            }
          }
        }
        return false;
      };
      
      removeNode(templateForm.value.structure, node.data.id);
      
      // Update display orders
      let order = 0;
      const updateOrders = (nodes: any[]) => {
        nodes.forEach((node, index) => {
          node.display_order = order++;
          if (node.children && node.children.length > 0) {
            updateOrders(node.children);
          }
        });
      };
      
      updateOrders(templateForm.value.structure);
      
      // Trigger reactivity
      templateForm.value.structure = [...templateForm.value.structure];
    };
    
    const moveLineUp = (node: any) => {
      const { parent, index } = findNodeAndParent(templateForm.value.structure, node.data.id);
      const nodes = parent ? parent.children : templateForm.value.structure;
      
      if (index > 0) {
        // Swap with previous node
        const temp = nodes[index - 1];
        nodes[index - 1] = nodes[index];
        nodes[index] = temp;
        
        // Update display orders
        nodes.forEach((n, i) => {
          n.display_order = i;
        });
        
        // Trigger reactivity
        templateForm.value.structure = [...templateForm.value.structure];
      }
    };
    
    const moveLineDown = (node: any) => {
      const { parent, index } = findNodeAndParent(templateForm.value.structure, node.data.id);
      const nodes = parent ? parent.children : templateForm.value.structure;
      
      if (index < nodes.length - 1) {
        // Swap with next node
        const temp = nodes[index + 1];
        nodes[index + 1] = nodes[index];
        nodes[index] = temp;
        
        // Update display orders
        nodes.forEach((n, i) => {
          n.display_order = i;
        });
        
        // Trigger reactivity
        templateForm.value.structure = [...templateForm.value.structure];
      }
    };
    
    const isFirstSibling = (node: any) => {
      const { parent, index } = findNodeAndParent(templateForm.value.structure, node.data.id);
      return index === 0;
    };
    
    const isLastSibling = (node: any) => {
      const { parent, index } = findNodeAndParent(templateForm.value.structure, node.data.id);
      const nodes = parent ? parent.children : templateForm.value.structure;
      return index === nodes.length - 1;
    };
    
    const findNodeById = (nodes: any[], id: string): any => {
      for (const node of nodes) {
        if (node.id === id) return node;
        if (node.children && node.children.length > 0) {
          const found = findNodeById(node.children, id);
          if (found) return found;
        }
      }
      return null;
    };
    
    const findNodeAndParent = (nodes: any[], id: string, parent: any = null, index = -1): { node: any, parent: any, index: number } => {
      for (let i = 0; i < nodes.length; i++) {
        if (nodes[i].id === id) {
          return { node: nodes[i], parent, index: i };
        }
        
        if (nodes[i].children && nodes[i].children.length > 0) {
          const found = findNodeAndParent(nodes[i].children, id, nodes[i], i);
          if (found.node) return found;
        }
      }
      return { node: null, parent: null, index: -1 };
    };
    
    const searchAccounts = (event: any) => {
      // In a real app, you would call an API to search for accounts
      setTimeout(() => {
        if (!event.query.trim().length) {
          filteredAccounts.value = [...accounts.value];
        } else {
          filteredAccounts.value = accounts.value.filter(account => {
            return (
              account.number.toLowerCase().includes(event.query.toLowerCase()) ||
              account.name.toLowerCase().includes(event.query.toLowerCase())
            );
          });
        }
      }, 250);
    };
    
    const buildTemplateTree = (lines: FinancialStatementLine[]) => {
      if (!lines || !lines.length) return [];
      
      const map = new Map<string, any>();
      const tree: any[] = [];
      
      // First pass: Create a map of all lines
      lines.forEach(line => {
        map.set(line.id, { ...line, children: [] });
      });
      
      // Second pass: Build the tree structure
      lines.forEach(line => {
        const node = map.get(line.id);
        if (line.parent_id && map.has(line.parent_id)) {
          const parent = map.get(line.parent_id);
          if (parent) {
            parent.children.push(node);
          }
        } else {
          tree.push(node);
        }
      });
      
      // Sort children by display_order
      const sortChildren = (nodes: any[]) => {
        nodes.sort((a, b) => a.display_order - b.display_order);
        nodes.forEach(node => {
          if (node.children && node.children.length > 0) {
            sortChildren(node.children);
          }
        });
      };
      
      sortChildren(tree);
      return tree;
    };
    
    const onNodeExpand = (node: any) => {
      expandedKeys.value[node.key] = true;
    };
    
    const onNodeCollapse = (node: any) => {
      delete expandedKeys.value[node.key];
    };
    
    const closeTemplateDialog = () => {
      showTemplateDialog.value = false;
      editingTemplate.value = null;
      templateForm.value = {
        name: '',
        description: '',
        statement_type: undefined,
        is_default: false,
        structure: []
      };
      submitted.value = false;
    };
    
    const saveTemplate = async () => {
      submitted.value = true;
      
      // Validate form
      if (!templateForm.value.name || !templateForm.value.statement_type) {
        toast.add({
          severity: 'warn',
          summary: 'Validation Error',
          detail: 'Please fill in all required fields',
          life: 3000
        });
        return;
      }
      
      try {
        saving.value = true;
        
        // Flatten the structure for API
        const flattenStructure = (nodes: any[], parentId: string | null = null, level = 0): any[] => {
          return nodes.reduce((acc, node, index) => {
            const { children, ...rest } = node;
            const newNode = {
              ...rest,
              parent_id: parentId,
              display_order: index,
              level
            };
            
            let result = [newNode];
            
            if (children && children.length > 0) {
              result = [...result, ...flattenStructure(children, node.id, level + 1)];
            }
            
            return [...acc, ...result];
          }, []);
        };
        
        const flattenedStructure = flattenStructure(templateForm.value.structure || []);
        
        const templateData = {
          ...templateForm.value,
          structure: flattenedStructure
        };
        
        let response: FinancialStatementTemplate;
        
        if (editingTemplate.value) {
          // Update existing template
          response = await financialStatementService.updateTemplate(
            editingTemplate.value.id,
            templateData
          );
          
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Template updated successfully',
            life: 3000
          });
        } else {
          // Create new template
          response = await financialStatementService.createTemplate(templateData);
          
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Template created successfully',
            life: 3000
          });
        }
        
        // If set as default, update the default template for this statement type
        if (templateForm.value.is_default && templateForm.value.statement_type) {
          try {
            await financialStatementService.setDefaultTemplate(
              response.id,
              templateForm.value.statement_type
            );
          } catch (error) {
            console.error('Error setting default template:', error);
            // Don't fail the whole operation if setting default fails
          }
        }
        
        // Reload templates
        await loadTemplates();
        
        // Close dialog
        closeTemplateDialog();
      } catch (error) {
        console.error('Error saving template:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to save template',
          life: 5000
        });
      } finally {
        saving.value = false;
      }
    };
    
    // Lifecycle hooks
    onMounted(() => {
      loadTemplates();
      
      // Load accounts for account selection
      // In a real app, you would call an API to load accounts
      // For now, we'll use mock data
      accounts.value = [
        { id: '1', number: '1000', name: 'Cash and Cash Equivalents' },
        { id: '2', number: '1100', name: 'Accounts Receivable' },
        { id: '3', number: '1200', name: 'Inventory' },
        { id: '4', number: '2000', name: 'Accounts Payable' },
        { id: '5', number: '3000', name: 'Common Stock' },
        { id: '6', number: '4000', name: 'Revenue' },
        { id: '7', number: '5000', name: 'Cost of Goods Sold' },
        { id: '8', number: '6000', name: 'Operating Expenses' },
      ];
      filteredAccounts.value = [...accounts.value];
    });
    
    return {
      // State
      templates,
      loading,
      saving,
      deleting,
      submitted,
      showTemplateDialog,
      editingTemplate,
      templateForm,
      expandedKeys,
      deleteDialog,
      previewDialog,
      filteredAccounts,
      
      // Computed
      showAccountNumberColumn,
      showFormulaColumn,
      statementTypeOptions,
      
      // Methods
      onPage,
      onSort,
      formatDate,
      formatStatementType,
      getLineStyle,
      editTemplate,
      previewTemplate,
      cloneTemplate,
      confirmDeleteTemplate,
      deleteTemplate,
      addLine,
      addChildLine,
      removeLine,
      moveLineUp,
      moveLineDown,
      isFirstSibling,
      isLastSibling,
      searchAccounts,
      buildTemplateTree,
      onNodeExpand,
      onNodeCollapse,
      closeTemplateDialog,
      saveTemplate
    };
  }
});
