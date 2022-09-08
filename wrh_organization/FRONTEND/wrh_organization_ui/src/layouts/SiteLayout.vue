<template>
  <v-app
    class="content-layout horizontal-nav"
    :class="{'content-full': appContentWidth === 'full'}"
  >
    <!-- Navbar -->
    <v-system-bar
      app
      height="64"
      :absolute="appBarType === 'static'"
      :class="[{'app-system-bar-boxed': appContentWidth === 'boxed'}, { 'bg-blur': appBarIsBlurred }]"
      class="app-system-bar"
    >
      <div class="navbar-content-container">
        <!-- Left Content: Search -->
        <div class="d-flex align-center">
          <v-app-bar-nav-icon
            v-if="$vuetify.breakpoint.mdAndDown"
          ></v-app-bar-nav-icon>
          <router-link
            :to="{name: $rns.ROOT}"
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
          <v-btn class="mr-4" outlined color="primary" :to="{name: $rns.DASHBOARD_HOME}">
            Sign In
          </v-btn>
          <app-bar-theme-switcher></app-bar-theme-switcher>
          <app-bar-user-menu v-if="$store.getters.isAuthenticated" class="ms-2"></app-bar-user-menu>
        </div>
      </div>
    </v-system-bar>

    <slot name="v-app-content"></slot>

    <v-main>
      <app-content-container>
        <slot></slot>
      </app-content-container>
    </v-main>
    <v-overlay
      :value="$store.state.app.shallContentShowOverlay"
      z-index="6"
      absolute
      class="content-overlay"
    ></v-overlay>

    <v-footer
      v-if="footerType !== 'hidden'"
      app
      inset
      :absolute="footerType === 'static'"
      padless
      :color="footerType === 'static' ? 'transparent' : null"
    >
      <v-col cols="12">
        <app-footer></app-footer>
      </v-col>
    </v-footer>
  </v-app>
</template>

<script>
import AppContentContainer from '@core/layouts/components/app-content-container/AppContentContainer.vue'
import useAppConfig from '@core/@app-config/useAppConfig'
import HorizontalNavMenu from '@/@core/layouts/components/horizontal-nav-menu/HorizontalNavMenu.vue'
import themeConfig from '@themeConfig'
import {mdiLogin} from '@mdi/js'
import AppBarThemeSwitcher from '@core/layouts/components/app-bar/AppBarThemeSwitcher.vue'
import AppFooter from "@/layouts/AppFooter";
import AppBarUserMenu from '@/components/AppBarUserMenu.vue'

export default {
  components: {
    AppContentContainer,
    HorizontalNavMenu,
    AppBarThemeSwitcher,
    AppFooter,
    AppBarUserMenu,
  },
  props: {
  },
  setup() {
    // eslint-disable-next-line object-curly-newline
    const { appBarType, appBarIsBlurred, footerType, appContentWidth } = useAppConfig()

    return {
      // App Config
      appName: themeConfig.app.name,
      appLogo: themeConfig.app.logo,
      appBarType,
      appBarIsBlurred,
      footerType,
      appContentWidth,
      icons: {
        mdiLogin,
      },
    }
  },
}
</script>

<style lang="scss" scoped>
@import '~@core/layouts/styles/_variables';

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

.app-content-container {
  padding: $content-padding-horizontal-navigation-menu;
  &.app-content-container-boxed {
    padding: $boxed-content-padding-horizontal-navigation-menu;
  }
}

@include theme(v-application) using ($material) {
  .app-system-bar {
    box-shadow: 0 1px 0 0 map-deep-get($material, 'dividers');
  }
  .v-app-bar.navigation-menu {
    border-bottom: thin solid map-deep-get($material, 'dividers');
  }
}

.v-application {
  // System bar
  .app-system-bar {
    padding: 0 !important;
    // border-bottom: thin solid rgba(94, 86, 105, 0.14);
    // box-shadow: 0 1px 0 0 rgba(0, 0, 0, 0.09);

    &.app-system-bar-boxed {
      ::v-deep > div:first-child {
        padding: $boxed-content-padding-horizontal-navigation-menu !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 1440px;
        margin-left: auto;
        margin-right: auto;
      }
    }
    ::v-deep > div:first-child {
      padding-left: $content-padding-vertical-navigation-menu !important;
      padding-right: $content-padding-vertical-navigation-menu !important;
    }
  }

  // App Bar
  .v-app-bar {
    ::v-deep .v-toolbar__content {
      padding: 0;
    }

    .horizontal-nav-menu {
      padding-left: $content-padding-vertical-navigation-menu !important;
      padding-right: $content-padding-vertical-navigation-menu !important;

      &.horizontal-nav-menu-boxed {
        width: 1440px;
        padding: $boxed-content-padding-horizontal-navigation-menu !important;
      }
    }
  }

  // @media screen and (max-width: 1711px) {
  //   margin-left: 1.5rem !important;
  //   margin-right: 1.5rem !important;
  // }

  // Footer
  .v-footer > div {
    max-width: 1440px;
    margin-left: auto;
    margin-right: auto;
    // Padding value is from `$boxed-content-padding-horizontal-navigation-menu`
    // We will keep top and buttom padding value of footer as it is
    padding-left: 3rem;
    padding-right: 3rem;

    @at-root .content-layout.content-full {
      .v-footer > div {
        max-width: unset;
        padding-left: $content-padding-vertical-navigation-menu !important;
        padding-right: $content-padding-vertical-navigation-menu !important;
      }
    }
  }
}
</style>
