<template>
  <layout-content-vertical-nav :nav-menu-items="navMenuItems">
    <slot></slot>

    <!-- Slot: Navbar -->
    <template #navbar="{ isVerticalNavMenuActive, toggleVerticalNavMenuActive }">
      <div
        class="navbar-content-container"
        :class="{'expanded-search': shallShowFullSearch}"
      >
        <!-- Left Content: Search -->
        <div class="d-flex align-center">
          <v-icon
            v-if="$vuetify.breakpoint.mdAndDown"
            class="me-3"
            @click="toggleVerticalNavMenuActive"
          >
            {{ icons.mdiMenu }}
          </v-icon>
          <app-bar-search
            :shall-show-full-search.sync="shallShowFullSearch"
            :data="appBarSearchData"
            :filter="searchFilterFunc"
            :search-query.sync="appBarSearchQuery"
            @update:shallShowFullSearch="handleShallShowFullSearchUpdate(isVerticalNavMenuActive, toggleVerticalNavMenuActive)"
          ></app-bar-search>
        </div>

        <!-- Right Content: I18n, Light/Dark, Notification & User Dropdown -->
        <div class="d-flex align-center right-row">
          <app-bar-theme-switcher></app-bar-theme-switcher>
          <app-bar-user-menu></app-bar-user-menu>
        </div>
      </div>
    </template>

    <!-- Slot: Footer -->
    <template #footer>
      <app-footer></app-footer>
    </template>
  </layout-content-vertical-nav>
</template>

<script>
import LayoutContentVerticalNav from '@/@core/layouts/variants/content/vertical-nav/LayoutContentVerticalNav.vue'

// App Bar Components
import AppBarSearch from '@core/layouts/components/app-bar/AppBarSearch.vue'
import AppBarUserMenu from '@/components/AppBarUserMenu.vue'
import AppBarThemeSwitcher from "@core/layouts/components/app-bar/AppBarThemeSwitcher";

import {mdiMenu, mdiHeartOutline, mdiHomeOutline, mdiCalendarMultiselect, mdiAccountGroup, mdiBike} from '@mdi/js'

import {getVuetify, useRouter} from '@core/utils'

// Search Data
import appBarSearchData from '@/assets/app-bar-search-data'

import {onMounted, onUnmounted, ref, watch} from '@vue/composition-api'
import AppFooter from "./AppFooter";
import {routeNames} from "@/router";
import store from '@/store';
import EventBus from "@/EventBus";

export default {
  components: {
    AppFooter,
    AppBarThemeSwitcher,
    LayoutContentVerticalNav,

    // App Bar Components
    AppBarSearch,
    AppBarUserMenu,
  },
  setup() {
    const $vuetify = getVuetify();
    const { router, route } = useRouter();

    const navMenuItems = [
      {
        title: 'Home',
        icon: mdiHomeOutline,
        to: routeNames.DASHBOARD_HOME,
      },
      {
        title: 'USA Events',
        icon: mdiCalendarMultiselect,
        to: routeNames.DASHBOARD_EVENTS,
      },
      {
        title: 'USA Club',
        icon: mdiAccountGroup,
        to: routeNames.DASHBOARD_CLUB,
      },
      {
        title: 'USA Rider',
        icon: mdiBike,
        to: routeNames.DASHBOARD_RIDER,
      },
    ];
    // Search
    const appBarSearchQuery = ref('')
    const shallShowFullSearch = ref(false)
    const maxItemsInGroup = 5
    const totalItemsInGroup = ref({
      pages: 0,
      files: 0,
      contacts: 0,
    })
    watch(appBarSearchQuery, () => {
      totalItemsInGroup.value = {
        pages: 0,
        files: 0,
        contacts: 0,
      }
    })

    const onSessionExpired = () => {
      router.replace({name: routeNames.AUTH, query: {next: route.value.fullPath}});
    };

    onMounted(() => {
      EventBus.on("user:session-expired", onSessionExpired);
      if (!store.getters.isAuthenticated) {
        onSessionExpired();
      }
    });
    onUnmounted(() => {
      EventBus.off("user:session-expired", onSessionExpired);
    });


    // NOTE: Update search function according to your usage
    const searchFilterFunc = (item, queryText, itemText) => {
      if (item.header || item.divider) return true

      const itemGroup = (() => {
        if (item.to !== undefined) return 'pages'
        if (item.size !== undefined) return 'files'
        if (item.email !== undefined) return 'contacts'

        return null
      })()

      const isMatched = itemText.toLocaleLowerCase().indexOf(queryText.toLocaleLowerCase()) > -1

      if (isMatched) {
        if (itemGroup === 'pages') totalItemsInGroup.value.pages += 1
        else if (itemGroup === 'files') totalItemsInGroup.value.files += 1
        else if (itemGroup === 'contacts') totalItemsInGroup.value.contacts += 1
      }

      return appBarSearchQuery.value && isMatched && totalItemsInGroup.value[itemGroup] <= maxItemsInGroup
    }

    // ? Handles case where in <lg vertical nav menu is open and search is triggered using hotkey then searchbox is hidden behind vertical nav menu overlaty
    const handleShallShowFullSearchUpdate = (isVerticalNavMenuActive, toggleVerticalNavMenuActive) => {
      if ($vuetify.breakpoint.mdAndDown && isVerticalNavMenuActive) {
        toggleVerticalNavMenuActive()
      }
    }

    return {
      navMenuItems,
      handleShallShowFullSearchUpdate,

      // Search
      appBarSearchQuery,
      shallShowFullSearch,
      appBarSearchData,
      searchFilterFunc,

      icons: {
        mdiMenu,
        mdiHeartOutline,
      },
    }
  },
}
</script>

<style lang="scss" scoped>
.navbar-content-container {
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-grow: 1;
  position: relative;
}

// ? Handle bg of autocomplete for blured appBar
.v-app-bar.bg-blur {
  .expanded-search {
    ::v-deep .app-bar-autocomplete-box div[role='combobox'] {
      background-color: transparent;
    }

    > .d-flex > button.v-icon {
      display: none;
    }

    // ===

    & > .right-row {
      visibility: hidden;
      opacity: 0;
    }

    ::v-deep .app-bar-search-toggler {
      visibility: hidden;
    }
  }
}
</style>
