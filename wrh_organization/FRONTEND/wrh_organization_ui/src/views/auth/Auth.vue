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
import {onMounted, ref} from '@vue/composition-api'
import Login from "@/views/auth/Login";
import Register from "@/views/auth/Register";
import ForgotPassword from "@/views/auth/ForgotPassword";
import {useRouter} from "@core/utils";

export default {
  components: {Register, Login, ForgotPassword},
  setup() {
    const pages = {'Login': 'Login', 'Register': 'Register', 'ForgotPassword': 'ForgotPassword'};
    const { route } = useRouter();
    const activePage = ref('Login');
    onMounted(() => {
      if (pages[route.value.params.page]) {
        activePage.value = pages[route.value.params.page] || 'Login' ;
      } else if (pages[route.value.query.page]) {
        activePage.value = pages[route.value.query.page] || 'Login' ;
      }
    });
    return {
      activePage,
    }

  },
}
</script>

<style lang="scss" scoped>
@import '@core/preset/preset/pages/auth.scss';
</style>
