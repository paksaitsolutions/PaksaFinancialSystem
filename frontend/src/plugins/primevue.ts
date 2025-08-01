import type { App } from 'vue';
import PrimeVue from 'primevue/config';
import Ripple from 'primevue/ripple';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import ToastService from 'primevue/toastservice';
import Toast from 'primevue/toast';
import ProgressSpinner from 'primevue/progressspinner';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import FileUpload from 'primevue/fileupload';
import Toolbar from 'primevue/toolbar';
import Menu from 'primevue/menu';
import Sidebar from 'primevue/sidebar';
import Divider from 'primevue/divider';
import SplitButton from 'primevue/splitbutton';
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import Chart from 'primevue/chart';

// Import PrimeVue styles at the top level
import 'primeicons/primeicons.css';
import '@/assets/primevue/theme.css';  // Local theme override
import 'primevue/resources/primevue.min.css';
import 'primeflex/primeflex.css';

export function setupPrimeVue(app: App) {
  app.use(PrimeVue, {
    ripple: true,
    inputStyle: 'filled',
    locale: {
      firstDayOfWeek: 1,
      dayNames: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
      dayNamesShort: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
      dayNamesMin: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
      monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
      monthNamesShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      today: 'Today',
      clear: 'Clear'
    }
  });

  // Add PrimeVue components
  app.component('Button', Button);
  app.component('InputText', InputText);
  app.component('Password', Password);
  app.component('Card', Card);
  app.component('DataTable', DataTable);
  app.component('Column', Column);
  app.component('Toast', Toast);
  app.component('ProgressSpinner', ProgressSpinner);
  app.component('Dialog', Dialog);
  app.component('Dropdown', Dropdown);
  app.component('Calendar', Calendar);
  app.component('InputNumber', InputNumber);
  app.component('Textarea', Textarea);
  app.component('FileUpload', FileUpload);
  app.component('Toolbar', Toolbar);
  app.component('Menu', Menu);
  app.component('Sidebar', Sidebar);
  app.component('Divider', Divider);
  app.component('SplitButton', SplitButton);
  app.component('TabView', TabView);
  app.component('TabPanel', TabPanel);
  app.component('Chart', Chart);

  // Add PrimeVue services
  app.use(ToastService);

  // Register directives
  app.directive('ripple', Ripple);

  // Styles are now imported at the top level
}
