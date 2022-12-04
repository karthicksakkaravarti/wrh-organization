<template>
  <layout-content-vertical-nav v-if="$vuetify.breakpoint.mdAndDown" :nav-menu-items="navMenuItems">
    <slot></slot>

    <!-- Slot: Navbar -->
    <template #navbar="{ isVerticalNavMenuActive, toggleVerticalNavMenuActive }">
      <div
        class="navbar-content-container"
      >
        <!-- Left Content: Search -->
        <div class="d-flex align-center">
          <v-icon class="me-3" v-if="navMenuItems && navMenuItems.length" @click="toggleVerticalNavMenuActive">
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

  <layout-content-horizontal-nav v-else :nav-menu-items="navMenuItems">
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
          <v-tooltip bottom v-else>
            <template #activator="{ on, attrs }">
              <v-btn v-bind="attrs" v-on="on" icon class="mr-4" :to="{name: $rns.DASHBOARD_HOME}">
                <v-icon class="mr-0">
                  {{icons.mdiApps}}
                </v-icon>
              </v-btn>
            </template>
            <span>Go to dashboard panel</span>
          </v-tooltip>
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

import { ref } from '@vue/composition-api'

import themeConfig from '@themeConfig'
import {mdiApps, mdiMenu, mdiHeartOutline, mdiLogin, mdiFlagCheckered, mdiCalendarMonth} from '@mdi/js'
import AppFooter from "@/layouts/AppFooter";
import {routeNames} from "@/router";
import AppBarSwitchOrg from "@/components/AppBarSwitchOrg";

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
    const navMenuItems = [
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
    ];

    return {
      navMenuItems,

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
