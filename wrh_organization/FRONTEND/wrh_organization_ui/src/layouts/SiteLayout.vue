<template>
  <layout-content-vertical-nav v-if="$vuetify.breakpoint.mdAndDown" :nav-menu-items="menuItems">
    <slot></slot>

    <!-- Slot: Navbar -->
    <template #navbar="{ isVerticalNavMenuActive, toggleVerticalNavMenuActive }">
      <div
        class="navbar-content-container"
      >
        <!-- Left Content: Search -->
        <div class="d-flex align-center">
          <v-icon class="me-3" v-if="menuItems && menuItems.length" @click="toggleVerticalNavMenuActive">
            {{ icons.mdiMenu }}
          </v-icon>
          <router-link
            :to="{name: $rns.PUBLIC_HOME}"
            class="d-flex align-center text-decoration-none"
          >
            <v-img
              :src="appLogo"
              max-height="30px"
              max-width="30px"
              alt="logo"
              contain
              class="me-3"
            ></v-img>
            <h2 class="app-title text--primary">
              {{ shortAppName }}
            </h2>
          </router-link>

        </div>

        <!-- Right Content: I18n, Light/Dark, Notification & User Dropdown -->
        <div class="d-flex align-center right-row">
          <app-bar-switch-org v-if="$store.getters.isAuthenticated"></app-bar-switch-org>
          <v-btn v-if="!$store.getters.isAuthenticated" outlined class="mr-4" color="primary" :to="{name: $rns.AUTH, query: {next: $route.fullPath}}">
            Sign In
          </v-btn>
          <app-bar-theme-switcher></app-bar-theme-switcher>
          <app-bar-user-menu v-if="$store.getters.isAuthenticated"></app-bar-user-menu>
        </div>
      </div>
    </template>

    <!-- Slot: Footer -->
    <template #footer>
      <app-footer></app-footer>
    </template>
  </layout-content-vertical-nav>

  <layout-content-horizontal-nav v-else :nav-menu-items="menuItems">
    <!-- Default Slot -->
    <slot></slot>

    <!-- Navbar -->
    <template #navbar>
      <div
        class="navbar-content-container"
      >
        <!-- Left Content: Search -->
        <div class="d-flex align-center">
          <router-link
            :to="{name: $rns.PUBLIC_HOME}"
            class="d-flex align-center text-decoration-none"
          >
            <v-img
              :src="appLogo"
              max-height="30px"
              max-width="30px"
              alt="logo"
              contain
              class="me-3"
            ></v-img>
            <h2 class="app-title text--primary">
              {{ appName }}
            </h2>
          </router-link>
        </div>

        <!-- Right Content: I18n, Light/Dark, Notification & User Dropdown -->
        <div class="d-flex align-center">
          <app-bar-switch-org v-if="$store.getters.isAuthenticated"></app-bar-switch-org>
          <v-btn v-if="!$store.getters.isAuthenticated" outlined class="mr-4" color="primary" :to="{name: $rns.AUTH, query: {next: $route.fullPath}}">
            Sign In
          </v-btn>
          <app-bar-theme-switcher></app-bar-theme-switcher>
          <app-bar-user-menu v-if="$store.getters.isAuthenticated" class="ms-2"></app-bar-user-menu>
        </div>
      </div>
      <v-overlay
        :value="$store.state.app.shallContentShowOverlay"
        z-index="5"
        absolute
        class="system-bar-overlay"
      ></v-overlay>
    </template>

    <!-- Slot: footer -->
    <template #footer>
      <app-footer></app-footer>
    </template>

  </layout-content-horizontal-nav>
</template>

<script>
import LayoutContentHorizontalNav from '@core/layouts/variants/content/horizontal-nav/LayoutContentHorizontalNav.vue'
import LayoutContentVerticalNav from '@core/layouts/variants/content/vertical-nav/LayoutContentVerticalNav'

// App Bar Components
import AppBarSearch from '@core/layouts/components/app-bar/AppBarSearch.vue'
import AppBarThemeSwitcher from '@core/layouts/components/app-bar/AppBarThemeSwitcher.vue'
import AppBarUserMenu from '@/components/AppBarUserMenu.vue'

import {computed, ref} from '@vue/composition-api'

import themeConfig from '@themeConfig'
import {
  mdiApps,
  mdiMenu,
  mdiHeartOutline,
  mdiLogin,
  mdiFlagCheckered,
  mdiCalendarMonth,
  mdiCalendarMultiselect,
  mdiWeb,
  mdiAccountGroup,
  mdiBike
} from '@mdi/js'
import AppFooter from "@/layouts/AppFooter";
import {routeNames} from "@/router";
import AppBarSwitchOrg from "@/components/AppBarSwitchOrg";
import {useRouter} from "@core/utils";

export default {
  components: {
    AppBarSwitchOrg,
    AppFooter,
    LayoutContentHorizontalNav,
    LayoutContentVerticalNav,

    // App Bar Components
    AppBarSearch,
    AppBarThemeSwitcher,
    AppBarUserMenu,
  },
  setup() {
    const { route } = useRouter();
    const navMenuItems = ref([
      {
        title: 'Race Results',
        icon: mdiFlagCheckered,
        to: routeNames.PUBLIC_RACE_RESULTS,
      },
      {
        title: 'Events',
        icon: mdiCalendarMonth,
        to: routeNames.PUBLIC_EVENTS,
      },
      // {
      //   title: 'USAC',
      //   icon: mdiWeb,
      //   children: [
      //     {
      //       title: 'USA Events',
      //       icon: mdiCalendarMultiselect,
      //       to: routeNames.USAC_EVENTS,
      //     },
      //     {
      //       title: 'USA Club',
      //       icon: mdiAccountGroup,
      //       to: routeNames.USAC_CLUB,
      //     },
      //     {
      //       title: 'USA Rider',
      //       icon: mdiBike,
      //       to: routeNames.USAC_RIDER,
      //     },
      //   ]
      // },
    ]);
    const menuItems = computed(() => {
      if (!!route.value.meta.layoutHideMenuItems) {
        return [];
      }
      return navMenuItems.value;
    });

    return {
      navMenuItems,
      menuItems,
      // App Config
      appName: themeConfig.app.name,
      appLogo: themeConfig.app.logo,
      shortAppName: themeConfig.app.shortName,

      // Icons
      icons: {
        mdiHeartOutline,
        mdiLogin,
        mdiApps,
        mdiMenu,
      },
    }
  },
}
</script>

<style lang="scss" scoped>
.app-title {
  font-size: 1.25rem;
  font-weight: 600;
}

.navbar-content-container {
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-grow: 1;
  position: relative;
}
</style>
