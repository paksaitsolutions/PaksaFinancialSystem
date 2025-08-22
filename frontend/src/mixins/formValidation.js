export default {
  data() {
    return {
      validationRules: {
        required: v => !!v || 'This field is required',
        email: v => !v || /.+@.+\..+/.test(v) || 'Email must be valid',
        minLength: (v, length) => !v || v.length >= length || `Must be at least ${length} characters`,
        passwordMatch: (v, match) => !v || v === match || 'Passwords do not match',
        phone: v => !v || /^\+?[0-9]{10,15}$/.test(v) || 'Phone number must be valid',
        numeric: v => !v || /^[0-9]+$/.test(v) || 'Must contain only numbers',
        alphanumeric: v => !v || /^[a-zA-Z0-9]+$/.test(v) || 'Must contain only letters and numbers'
      }
    }
  },
  methods: {
    validate(rules, value) {
      for (const rule of rules) {
        const result = typeof rule === 'function' 
          ? rule(value)
          : this.validationRules[rule](value);
          
        if (result !== true) return result;
      }
      return true;
    }
  }
}