<template>

  <component
    :is="resolveLayoutVariant"
    :class="`skin-variant--${appSkinVariant}`"
    v-if="resolveLayoutVariant"
  >
    <transition
      :name="appRouteTransition"
      mode="out-in"
      appear
    >
      <router-view :key="$route.fullPath"></router-view>
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
import {appendLinkToHeader, appendStyleToHeader, getQueryParams, notifyDefaultServerError} from "@/composables/utils";
import AppVersionAlert from "@/components/AppVersionAlert";

export default {
  components: {
    AppVersionAlert,
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
      if (!route.value || !route.value.name) {
        return
      }
      return route.value.meta.layout || 'PublicLayout';
    });

    onMounted(() => {
      EventBus.on("user:session-expired", onSessionExpired);
      EventBus.on("user:session-refresh", onSessionRefresh);
      EventBus.on("ui:mismatch-version", onMismatchVersion);
      const externalCss = getQueryParams('_css', window.location);
      const externalStyle = getQueryParams('_style', window.location);
      if (externalCss) {
        appendLinkToHeader(decodeURIComponent(externalCss));
      }
      if (externalStyle) {
        appendStyleToHeader(decodeURIComponent(externalStyle));
      }
    });

    onUnmounted(() => {
      EventBus.off("user:session-expired", onSessionExpired);
      EventBus.off("user:session-refresh", onSessionRefresh);
      EventBus.off("ui:mismatch-version", onMismatchVersion);
    });


    useDynamicVh()

    return {
      resolveLayoutVariant,
      appSkinVariant,
      appRouteTransition,
      mismatchVersion,
      newAppVersion,
    }
  },
}
</script>
