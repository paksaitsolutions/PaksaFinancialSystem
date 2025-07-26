<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Help Topics</v-card-title>
          <v-list>
            <v-list-item
              v-for="topic in helpTopics"
              :key="topic.id"
              @click="selectedTopic = topic"
              :class="{ 'v-list-item--active': selectedTopic?.id === topic.id }"
            >
              <template v-slot:prepend>
                <v-icon>{{ topic.icon }}</v-icon>
              </template>
              <v-list-item-title>{{ topic.title }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card>
        
        <v-card class="mt-4">
          <v-card-title>Quick Actions</v-card-title>
          <v-card-text>
            <v-btn block class="mb-2" @click="openVideoTutorial">
              <v-icon left>mdi-play-circle</v-icon>
              Video Tutorials
            </v-btn>
            <v-btn block class="mb-2" @click="downloadUserGuide">
              <v-icon left>mdi-download</v-icon>
              Download User Guide
            </v-btn>
            <v-btn block @click="contactSupport">
              <v-icon left>mdi-help-circle</v-icon>
              Contact Support
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="9">
        <v-card v-if="selectedTopic">
          <v-card-title>
            <v-icon left>{{ selectedTopic.icon }}</v-icon>
            {{ selectedTopic.title }}
          </v-card-title>
          <v-card-text>
            <div v-html="selectedTopic.content"></div>
            
            <v-divider class="my-4" />
            
            <h3 class="mb-3">Related Articles</h3>
            <v-chip-group>
              <v-chip
                v-for="related in selectedTopic.relatedTopics"
                :key="related"
                @click="selectRelatedTopic(related)"
                small
              >
                {{ related }}
              </v-chip>
            </v-chip-group>
            
            <v-divider class="my-4" />
            
            <h3 class="mb-3">Was this helpful?</h3>
            <v-btn-toggle v-model="feedback" mandatory>
              <v-btn value="yes" color="success">
                <v-icon>mdi-thumb-up</v-icon>
                Yes
              </v-btn>
              <v-btn value="no" color="error">
                <v-icon>mdi-thumb-down</v-icon>
                No
              </v-btn>
            </v-btn-toggle>
            
            <v-textarea
              v-if="feedback === 'no'"
              v-model="feedbackComment"
              label="How can we improve this article?"
              rows="3"
              class="mt-3"
            />
            
            <v-btn
              v-if="feedback"
              @click="submitFeedback"
              color="primary"
              class="mt-3"
            >
              Submit Feedback
            </v-btn>
          </v-card-text>
        </v-card>
        
        <v-card v-else>
          <v-card-title>General Ledger Help Center</v-card-title>
          <v-card-text>
            <p class="text-h6 mb-4">Welcome to the General Ledger Help Center</p>
            <p>Select a topic from the left sidebar to get detailed information about using the General Ledger module.</p>
            
            <v-row class="mt-6">
              <v-col cols="12" md="4" v-for="category in helpCategories" :key="category.title">
                <v-card outlined>
                  <v-card-text class="text-center">
                    <v-icon size="48" color="primary">{{ category.icon }}</v-icon>
                    <h3 class="mt-2">{{ category.title }}</h3>
                    <p>{{ category.description }}</p>
                    <v-btn @click="selectCategory(category)" color="primary" small>
                      Learn More
                    </v-btn>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Video Tutorial Dialog -->
    <v-dialog v-model="showVideoDialog" max-width="800">
      <v-card>
        <v-card-title>Video Tutorials</v-card-title>
        <v-card-text>
          <v-list>
            <v-list-item
              v-for="video in videoTutorials"
              :key="video.id"
              @click="playVideo(video)"
            >
              <template v-slot:prepend>
                <v-icon>mdi-play-circle</v-icon>
              </template>
              <v-list-item-title>{{ video.title }}</v-list-item-title>
              <v-list-item-subtitle>{{ video.duration }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showVideoDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useGLHelpStore } from '../store/gl-help'

const glHelpStore = useGLHelpStore()
const selectedTopic = ref(null)
const feedback = ref(null)
const feedbackComment = ref('')
const showVideoDialog = ref(false)

const helpCategories = [
  {
    title: 'Getting Started',
    description: 'Learn the basics of the General Ledger module',
    icon: 'mdi-rocket-launch'
  },
  {
    title: 'Chart of Accounts',
    description: 'Manage your chart of accounts effectively',
    icon: 'mdi-file-tree'
  },
  {
    title: 'Journal Entries',
    description: 'Create and manage journal entries',
    icon: 'mdi-book-open-page-variant'
  },
  {
    title: 'Financial Reports',
    description: 'Generate and customize financial reports',
    icon: 'mdi-chart-line'
  },
  {
    title: 'Period Closing',
    description: 'Learn about period-end closing procedures',
    icon: 'mdi-calendar-check'
  },
  {
    title: 'Troubleshooting',
    description: 'Common issues and solutions',
    icon: 'mdi-tools'
  }
]

const helpTopics = ref([
  {
    id: 1,
    title: 'Getting Started with GL',
    icon: 'mdi-rocket-launch',
    content: `
      <h3>Welcome to the General Ledger Module</h3>
      <p>The General Ledger is the foundation of your financial system. Here's how to get started:</p>
      <ol>
        <li><strong>Set up your Chart of Accounts:</strong> Navigate to the Chart of Accounts section to create your account structure.</li>
        <li><strong>Configure GL Settings:</strong> Set your default currency, fiscal year, and other preferences.</li>
        <li><strong>Create Journal Entries:</strong> Start recording your financial transactions.</li>
        <li><strong>Generate Reports:</strong> Use the reporting dashboard to view your financial position.</li>
      </ol>
      <h4>Key Features:</h4>
      <ul>
        <li>Multi-currency support</li>
        <li>Automated journal entries</li>
        <li>Real-time reporting</li>
        <li>Period-end closing</li>
        <li>Audit trail</li>
      </ul>
    `,
    relatedTopics: ['Chart of Accounts Setup', 'Journal Entry Basics', 'GL Settings']
  },
  {
    id: 2,
    title: 'Chart of Accounts Setup',
    icon: 'mdi-file-tree',
    content: `
      <h3>Setting Up Your Chart of Accounts</h3>
      <p>A well-structured chart of accounts is essential for accurate financial reporting.</p>
      <h4>Account Types:</h4>
      <ul>
        <li><strong>Assets:</strong> What your company owns (Cash, Accounts Receivable, Equipment)</li>
        <li><strong>Liabilities:</strong> What your company owes (Accounts Payable, Loans)</li>
        <li><strong>Equity:</strong> Owner's stake in the company</li>
        <li><strong>Revenue:</strong> Income from business operations</li>
        <li><strong>Expenses:</strong> Costs of doing business</li>
      </ul>
      <h4>Best Practices:</h4>
      <ul>
        <li>Use a consistent numbering system</li>
        <li>Keep account names clear and descriptive</li>
        <li>Group similar accounts together</li>
        <li>Plan for future growth</li>
      </ul>
    `,
    relatedTopics: ['Account Numbering', 'Account Categories', 'Account Hierarchies']
  },
  {
    id: 3,
    title: 'Creating Journal Entries',
    icon: 'mdi-book-open-page-variant',
    content: `
      <h3>Journal Entry Fundamentals</h3>
      <p>Journal entries are the building blocks of your financial records.</p>
      <h4>Double-Entry Accounting:</h4>
      <p>Every transaction affects at least two accounts, and total debits must equal total credits.</p>
      <h4>Creating an Entry:</h4>
      <ol>
        <li>Navigate to Journal Entries</li>
        <li>Click "New Entry"</li>
        <li>Enter the transaction date</li>
        <li>Add description</li>
        <li>Select accounts and enter amounts</li>
        <li>Verify debits equal credits</li>
        <li>Save and post</li>
      </ol>
      <h4>Entry Types:</h4>
      <ul>
        <li>Manual entries</li>
        <li>Recurring entries</li>
        <li>Adjusting entries</li>
        <li>Closing entries</li>
      </ul>
    `,
    relatedTopics: ['Double-Entry Accounting', 'Recurring Entries', 'Entry Approval']
  }
])

const videoTutorials = [
  { id: 1, title: 'GL Module Overview', duration: '5:30' },
  { id: 2, title: 'Setting Up Chart of Accounts', duration: '8:15' },
  { id: 3, title: 'Creating Journal Entries', duration: '6:45' },
  { id: 4, title: 'Generating Financial Reports', duration: '7:20' },
  { id: 5, title: 'Period-End Closing Process', duration: '12:10' }
]

const selectCategory = (category) => {
  const topic = helpTopics.value.find(t => t.title.includes(category.title.split(' ')[0]))
  if (topic) {
    selectedTopic.value = topic
  }
}

const selectRelatedTopic = (topicTitle) => {
  const topic = helpTopics.value.find(t => t.title === topicTitle)
  if (topic) {
    selectedTopic.value = topic
  }
}

const openVideoTutorial = () => {
  showVideoDialog.value = true
}

const playVideo = (video) => {
  // Implement video playback
  console.log('Playing video:', video.title)
}

const downloadUserGuide = () => {
  // Implement user guide download
  const link = document.createElement('a')
  link.href = '/docs/gl-user-guide.pdf'
  link.download = 'GL-User-Guide.pdf'
  link.click()
}

const contactSupport = () => {
  // Implement support contact
  window.open('mailto:support@paksa.com.pk?subject=GL Module Support')
}

const submitFeedback = async () => {
  await glHelpStore.submitFeedback({
    topicId: selectedTopic.value.id,
    helpful: feedback.value === 'yes',
    comment: feedbackComment.value
  })
  feedback.value = null
  feedbackComment.value = ''
}

onMounted(() => {
  // Load help content
  selectedTopic.value = helpTopics.value[0]
})
</script>