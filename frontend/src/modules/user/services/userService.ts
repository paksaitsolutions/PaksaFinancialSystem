import axios from 'axios'

export async function inviteUser({ email, firstName, lastName, roleId, companyId }: {
  email: string,
  firstName: string,
  lastName: string,
  roleId: string,
  companyId: string
}) {
  return axios.post('/users/invite', {
    email,
    first_name: firstName,
    last_name: lastName,
    role_id: roleId,
    password: 'temporary' // Backend should send invitation email to set password
  }, {
    params: { company_id: companyId }
  })
}
