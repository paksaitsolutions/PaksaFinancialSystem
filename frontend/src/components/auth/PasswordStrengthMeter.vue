<template>
  <div class="password-strength">
    <div class="strength-meter">
      <div 
        class="strength-meter-fill" 
        :style="{ width: score + '%', backgroundColor: strengthColor }"
      ></div>
    </div>
    <div class="strength-text" :style="{ color: strengthColor }">
      {{ strengthText }}
    </div>
  </div>
</template>

<script>
export default {
  props: {
    password: {
      type: String,
      required: true
    }
  },
  computed: {
    score() {
      let score = 0;
      
      // Length check
      if (this.password.length > 0) score += 20;
      if (this.password.length >= 8) score += 20;
      
      // Complexity checks
      if (/[A-Z]/.test(this.password)) score += 20;
      if (/[0-9]/.test(this.password)) score += 20;
      if (/[^A-Za-z0-9]/.test(this.password)) score += 20;
      
      return score;
    },
    strengthText() {
      if (this.score < 40) return 'Weak';
      if (this.score < 80) return 'Medium';
      return 'Strong';
    },
    strengthColor() {
      if (this.score < 40) return '#FF5252';
      if (this.score < 80) return '#FFC107';
      return '#4CAF50';
    }
  }
}
</script>

<style scoped>
.password-strength {
  margin-top: 5px;
  margin-bottom: 15px;
}

.strength-meter {
  height: 4px;
  background-color: #DDD;
  border-radius: 2px;
  margin-bottom: 5px;
}

.strength-meter-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease-in-out, background-color 0.5s ease-in-out;
}

.strength-text {
  font-size: 12px;
  text-align: right;
}
</style>