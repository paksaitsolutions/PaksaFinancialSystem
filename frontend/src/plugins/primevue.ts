import type { App } from 'vue'
import PrimeVue from 'primevue/config'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'
import RadioButton from 'primevue/radiobutton'
import Menu from 'primevue/menu'
import Menubar from 'primevue/menubar'
import Sidebar from 'primevue/sidebar'
import Toast from 'primevue/toast'
import ToastService from 'primevue/toastservice'
import ConfirmDialog from 'primevue/confirmdialog'
import ConfirmationService from 'primevue/confirmationservice'
import Toolbar from 'primevue/toolbar'
import SplitButton from 'primevue/splitbutton'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Chart from 'primevue/chart'
import ProgressBar from 'primevue/progressbar'
import Badge from 'primevue/badge'
import Avatar from 'primevue/avatar'
import Chip from 'primevue/chip'
import Tag from 'primevue/tag'
import Message from 'primevue/message'
import OverlayPanel from 'primevue/overlaypanel'
import Panel from 'primevue/panel'
import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'
import Breadcrumb from 'primevue/breadcrumb'
import Steps from 'primevue/steps'
import FileUpload from 'primevue/fileupload'
import MultiSelect from 'primevue/multiselect'
import AutoComplete from 'primevue/autocomplete'
import Slider from 'primevue/slider'
import Rating from 'primevue/rating'
import SelectButton from 'primevue/selectbutton'
import ToggleButton from 'primevue/togglebutton'
import InputSwitch from 'primevue/inputswitch'
import Divider from 'primevue/divider'
import Skeleton from 'primevue/skeleton'
import ScrollPanel from 'primevue/scrollpanel'
import Splitter from 'primevue/splitter'
import SplitterPanel from 'primevue/splitterpanel'
import Tree from 'primevue/tree'
import TreeTable from 'primevue/treetable'
import Paginator from 'primevue/paginator'
import Image from 'primevue/image'
import InlineMessage from 'primevue/inlinemessage'
import ProgressSpinner from 'primevue/progressspinner'
import Ripple from 'primevue/ripple'
import StyleClass from 'primevue/styleclass'
import Tooltip from 'primevue/tooltip'

export function setupPrimeVue(app: App) {
  app.use(PrimeVue)
  app.use(ToastService)
  app.use(ConfirmationService)

  // Register directives
  app.directive('ripple', Ripple)
  app.directive('styleclass', StyleClass)
  app.directive('tooltip', Tooltip)

  // Register components
  app.component('Button', Button)
  app.component('InputText', InputText)
  app.component('Password', Password)
  app.component('Card', Card)
  app.component('DataTable', DataTable)
  app.component('Column', Column)
  app.component('Dialog', Dialog)
  app.component('Dropdown', Dropdown)
  app.component('Calendar', Calendar)
  app.component('InputNumber', InputNumber)
  app.component('Textarea', Textarea)
  app.component('Checkbox', Checkbox)
  app.component('RadioButton', RadioButton)
  app.component('Menu', Menu)
  app.component('Menubar', Menubar)
  app.component('Sidebar', Sidebar)
  app.component('Toast', Toast)
  app.component('ConfirmDialog', ConfirmDialog)
  app.component('Toolbar', Toolbar)
  app.component('SplitButton', SplitButton)
  app.component('TabView', TabView)
  app.component('TabPanel', TabPanel)
  app.component('Chart', Chart)
  app.component('ProgressBar', ProgressBar)
  app.component('Badge', Badge)
  app.component('Avatar', Avatar)
  app.component('Chip', Chip)
  app.component('Tag', Tag)
  app.component('Message', Message)
  app.component('OverlayPanel', OverlayPanel)
  app.component('Panel', Panel)
  app.component('Accordion', Accordion)
  app.component('AccordionTab', AccordionTab)
  app.component('Breadcrumb', Breadcrumb)
  app.component('Steps', Steps)
  app.component('FileUpload', FileUpload)
  app.component('MultiSelect', MultiSelect)
  app.component('AutoComplete', AutoComplete)
  app.component('Slider', Slider)
  app.component('Rating', Rating)
  app.component('SelectButton', SelectButton)
  app.component('ToggleButton', ToggleButton)
  app.component('InputSwitch', InputSwitch)
  app.component('Divider', Divider)
  app.component('Skeleton', Skeleton)
  app.component('ScrollPanel', ScrollPanel)
  
  // Register components and directives only if not already registered
  if (!('tooltip' in app._context.directives)) {
    app.directive('tooltip', Tooltip);
  }
  app.component('Splitter', Splitter)
  app.component('SplitterPanel', SplitterPanel)
  app.component('Tree', Tree)
  app.component('TreeTable', TreeTable)
  app.component('Paginator', Paginator)
  app.component('Image', Image)
  app.component('InlineMessage', InlineMessage)
  app.component('ProgressSpinner', ProgressSpinner)
}