<template>
  <v-dialog :model-value="dialog" @update:model-value="$emit('update:dialog', $event)" max-width="500">
    <v-card>
      <v-card-title>Invite User</v-card-title>
      <v-card-text>
        <v-form ref="form" @submit.prevent="inviteUser">
          <v-text-field v-model="email" label="Email" required></v-text-field>
          <v-text-field v-model="firstName" label="First Name" required></v-text-field>
          <v-text-field v-model="lastName" label="Last Name" required></v-text-field>
          <v-select v-model="roleId" :items="roles" item-text="name" item-value="id" label="Role" required></v-select>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="inviteUser">Invite</v-btn>
        <v-btn text @click="$emit('update:dialog', false)">Cancel</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'UserInviteDialog',
  props: {
    dialog: Boolean,
    companyId: String,
    roles: Array
  },
  emits: ['update:dialog', 'invited'],
  data() {
    return {
      email: '',
      firstName: '',
      lastName: '',
      roleId: ''
    }
  },
  methods: {
    async inviteUser() {
      // Call backend API to invite user
      await this.$axios.post('/users/invite', {
        email: this.email,
        first_name: this.firstName,
        last_name: this.lastName,
        role_id: this.roleId,
        password: 'temporary' // Backend should send invitation email to set password
      }, {
        params: { company_id: this.companyId }
      })
      this.$emit('invited')
      this.$emit('update:dialog', false)
    }
  }
}
</script>
