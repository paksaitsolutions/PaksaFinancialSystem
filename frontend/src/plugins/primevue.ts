import { App } from 'vue'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import Tooltip from 'primevue/tooltip'

// Components
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Tag from 'primevue/tag'
import Divider from 'primevue/divider'
import ProgressSpinner from 'primevue/progressspinner'
import Chip from 'primevue/chip'
import Chart from 'primevue/chart'
import Checkbox from 'primevue/checkbox'
import Calendar from 'primevue/calendar'
import RadioButton from 'primevue/radiobutton'
import SelectButton from 'primevue/selectbutton'
import MultiSelect from 'primevue/multiselect'
import TreeSelect from 'primevue/treeselect'
import AutoComplete from 'primevue/autocomplete'
import ConfirmDialog from 'primevue/confirmdialog'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import FileUpload from 'primevue/fileupload'
import Message from 'primevue/message'
import Toast from 'primevue/toast'

export default {
  install(app: App) {
    app.use(PrimeVue)
    app.use(ToastService)
    app.use(ConfirmationService)
    
    // Directives
    app.directive('tooltip', Tooltip)
    
    // Global components
    app.component('Button', Button)
    app.component('InputText', InputText)
    app.component('Password', Password)
    app.component('InputNumber', InputNumber)
    app.component('Textarea', Textarea)
    app.component('Dropdown', Dropdown)
    app.component('Card', Card)
    app.component('DataTable', DataTable)
    app.component('Column', Column)
    app.component('Dialog', Dialog)
    app.component('Tag', Tag)
    app.component('Divider', Divider)
    app.component('ProgressSpinner', ProgressSpinner)
    app.component('Chip', Chip)
    app.component('Chart', Chart)
    app.component('Checkbox', Checkbox)
    app.component('Calendar', Calendar)
    app.component('RadioButton', RadioButton)
    app.component('SelectButton', SelectButton)
    app.component('MultiSelect', MultiSelect)
    app.component('TreeSelect', TreeSelect)
    app.component('AutoComplete', AutoComplete)
    app.component('ConfirmDialog', ConfirmDialog)
    app.component('TabView', TabView)
    app.component('TabPanel', TabPanel)
    app.component('FileUpload', FileUpload)
    app.component('Message', Message)
    app.component('Toast', Toast)
  }
}