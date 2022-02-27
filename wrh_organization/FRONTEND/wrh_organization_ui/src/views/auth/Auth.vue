<template>
  <div class="auth-wrapper auth-v1">
    <div class="auth-inner">
      <v-slide-x-transition :hide-on-leave="true">
        <component :key="activePage" :is="activePage" @change-page="(p) => {activePage=p}"></component>
      </v-slide-x-transition>
    </div>
  </div>
</template>

<script>
// eslint-disable-next-line object-curly-newline
import { ref } from '@vue/composition-api'
import Login from "@/views/auth/Login";
import Register from "@/views/auth/Register";
import ForgotPassword from "@/views/auth/ForgotPassword";

export default {
  components: {Register, Login, ForgotPassword},
  setup() {
    const activePage = ref("Login");
    return {
      activePage,
    }
  },
}
</script>

<style lang="scss" scoped>
@import '@core/preset/preset/pages/auth.scss';
</style>
