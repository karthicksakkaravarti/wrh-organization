<template>

  <component
    :is="loginRequired? 'BlankLayout': resolveLayoutVariant"
    :class="`skin-variant--${appSkinVariant}`"
  >
    <transition
      :name="appRouteTransition"
      mode="out-in"
      appear
    >
      <Auth v-if="loginRequired"></Auth>
      <router-view v-else></router-view>
    </transition>
    <app-version-alert v-if="mismatchVersion" :new-version="newAppVersion">
    </app-version-alert>
  </component>
</template>

<script>
// eslint-disable-next-line object-curly-newline
import { computed, onMounted, onUnmounted, ref } from '@vue/composition-api'
// eslint-disable-next-line import/no-unresolved
import useAppConfig from '@core/@app-config/useAppConfig'
import { useRouter } from '@core/utils'
import { useLayout } from '@core/layouts/composable/useLayout'
import axios from '@/axios';
import store from '@/store';
import EventBus from '@/EventBus'

import SiteLayout from '@/layouts/SiteLayout'
import BlankLayout from '@/layouts/BlankLayout'
import PublicLayout from '@/layouts/PublicLayout'
import DashboardLayout from '@/layouts/DashboardLayout'

// Dynamic vh
import useDynamicVh from '@core/utils/useDynamicVh'
import Auth from "@/views/auth/Auth";
import {notifyDefaultServerError} from "@/composables/utils";
import AppVersionAlert from "@/components/AppVersionAlert";

export default {
  components: {
    AppVersionAlert,
    Auth,
    BlankLayout,
    SiteLayout,
    PublicLayout,
    DashboardLayout,
  },
  setup() {
    const mismatchVersion = ref(false);
    const newAppVersion = ref(null);
    const { route } = useRouter();
    const { appContentLayoutNav, appSkinVariant, appRouteTransition } = useAppConfig();
    const { handleBreakpointLayoutSwitch } = useLayout();
    const onSessionRefresh = () => {
      axios.get("account/session").then(
        (response) => {
          store.state.currentUser = response.data;
        }, (error) => {
          notifyDefaultServerError(error, true);
        }
      );
      // axios.get("bycing_org/member/me").then(
      //   (response) => {
      //     store.state.currentMember = response.data;
      //   },
      //   (error) => {
      //     notifyDefaultServerError(error, true);
      //   }
      // );

    };
    const onSessionExpired = () => {
      store.state.currentUser = {};
    };
    const onMismatchVersion = (newVersion) => {
      mismatchVersion.value = true;
      newAppVersion.value = newVersion;
    };

    handleBreakpointLayoutSwitch();

    const resolveLayoutVariant = computed(() => {
      return route.value.meta.layout || 'PublicLayout';
    });
    const loginRequired = computed(() => {
      return (resolveLayoutVariant.value === 'DashboardLayout' && !store.getters.isAuthenticated);
    });

    onMounted(() => {
      EventBus.on("user:session-expired", onSessionExpired);
      EventBus.on("user:session-refresh", onSessionRefresh);
      EventBus.on("ui:mismatch-version", onMismatchVersion);

    });

    onUnmounted(() => {
      EventBus.off("user:session-expired", onSessionExpired);
      EventBus.off("user:session-refresh", onSessionRefresh);
      EventBus.off("ui:mismatch-version", onMismatchVersion);
    });


    useDynamicVh()

    return {
      resolveLayoutVariant,
      loginRequired,
      appSkinVariant,
      appRouteTransition,
      mismatchVersion,
      newAppVersion,
    }
  },
}
</script>
