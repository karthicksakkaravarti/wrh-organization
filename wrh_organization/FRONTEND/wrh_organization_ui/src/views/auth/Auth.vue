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
import {getQueryParams} from "@/composables/utils";

export default {
  components: {Register, Login, ForgotPassword},
  setup() {
    var pageParam = getQueryParams('page', window.location.href);
    var pages = {'Login': 'Login', 'Register': 'Register', 'ForgotPassword': 'ForgotPassword'}
    var defaultPage = pages[pageParam] || 'Login';
    const activePage = ref(defaultPage);
    onMounted(() => {
      if (pages[route.value.params.page]) {
        activePage.value = defaultPage[route.value.params.page] || 'Login' ;
      }
      loadMemberData();
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
