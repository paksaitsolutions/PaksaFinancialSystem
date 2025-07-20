import PrimeVue from 'primevue/config';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import Toast from 'primevue/toast';
import ToastService from 'primevue/toastservice';
import Toolbar from 'primevue/toolbar';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import Checkbox from 'primevue/checkbox';
import RadioButton from 'primevue/radiobutton';
import InputSwitch from 'primevue/inputswitch';
import ProgressSpinner from 'primevue/progressspinner';
import ProgressBar from 'primevue/progressbar';
import Tag from 'primevue/tag';
import Badge from 'primevue/badge';
import Card from 'primevue/card';
import Tooltip from 'primevue/tooltip';
import Menu from 'primevue/menu';
import Panel from 'primevue/panel';
import Divider from 'primevue/divider';
import FileUpload from 'primevue/fileupload';
import MultiSelect from 'primevue/multiselect';
import Calendar from 'primevue/calendar';
import SelectButton from 'primevue/selectbutton';
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import Tree from 'primevue/tree';
import TreeTable from 'primevue/treetable';
import ConfirmDialog from 'primevue/confirmdialog';
import ConfirmationService from 'primevue/confirmationservice';
import OverlayPanel from 'primevue/overlaypanel';
import Skeleton from 'primevue/skeleton';
import VirtualScroller from 'primevue/virtualscroller';

// Import PrimeVue theme
import 'primevue/resources/themes/saga-blue/theme.css';
// Import PrimeVue core styles
import 'primevue/resources/primevue.min.css';
// Import PrimeIcons
import 'primeicons/primeicons.css';

export default {
  install(app: any) {
    // Use PrimeVue with ripple effect
    app.use(PrimeVue, { ripple: true });
    
    // Use Toast and Confirmation services
    app.use(ToastService);
    app.use(ConfirmationService);
    
    // Register components
    const components = {
      Button,
      InputText,
      DataTable,
      Column,
      Dialog,
      Dropdown,
      Toast,
      Toolbar,
      InputNumber,
      Textarea,
      Checkbox,
      RadioButton,
      InputSwitch,
      ProgressSpinner,
      ProgressBar,
      Tag,
      Badge,
      Card,
      Menu,
      Panel,
      Divider,
      FileUpload,
      MultiSelect,
      Calendar,
      SelectButton,
      TabView,
      TabPanel,
      Tree,
      TreeTable,
      ConfirmDialog,
      OverlayPanel,
      Skeleton,
      VirtualScroller
    };
    
    Object.entries(components).forEach(([name, component]) => {
      app.component(`P${name}`, component);
    });
    
    // Register global directives
    app.directive('tooltip', Tooltip);
  }
};
