module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    es2022: true
  },
  extends: [
    'eslint:recommended',
    '@vue/eslint-config-typescript/recommended',
    '@vue/eslint-config-prettier'
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
    parser: '@typescript-eslint/parser'
  },
  plugins: ['@typescript-eslint', 'vue'],
  rules: {
    // Vue specific rules
    'vue/multi-word-component-names': 'off',
    'vue/no-unused-vars': 'error',
    'vue/no-unused-components': 'warn',
    'vue/require-default-prop': 'off',
    'vue/require-prop-types': 'off',
    
    // TypeScript rules
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/no-non-null-assertion': 'warn',
    
    // General rules
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'prefer-const': 'error',
    'no-var': 'error',
    'eqeqeq': 'error',
    'curly': 'error',
    'no-trailing-spaces': 'error',
    'comma-dangle': ['error', 'never'],
    'semi': ['error', 'never'],
    'quotes': ['error', 'single'],
    'indent': ['error', 2],
    'no-multiple-empty-lines': ['error', { max: 1 }],
    'eol-last': 'error'
  },
  overrides: [
    {
      files: ['*.vue'],
      rules: {
        'indent': 'off'
      }
    }
  ]
}