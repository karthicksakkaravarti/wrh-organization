<script>
import {mdiHomeOutline, mdiCalendarMultiselect, mdiAccountGroup, mdiBike} from '@mdi/js'

import {getVuetify, useRouter} from '@core/utils'

import {computed, onMounted, onUnmounted, ref} from '@vue/composition-api'
import {routeNames} from "@/router";
import store from '@/store';
import EventBus from "@/EventBus";
import SiteLayout from "@/layouts/SiteLayout.vue";

export default {
  extends: SiteLayout,
  components: {},
  setup() {
    const $vuetify = getVuetify();
    const { router, route } = useRouter();

    // const navMenuItems = [
    //   {
    //     title: 'Home',
    //     icon: mdiHomeOutline,
    //     to: routeNames.ROOT,
    //   },
    //   {
    //     title: 'USA Events',
    //     icon: mdiCalendarMultiselect,
    //     to: routeNames.USAC_EVENTS,
    //   },
    //   {
    //     title: 'USA Club',
    //     icon: mdiAccountGroup,
    //     to: routeNames.USAC_CLUB,
    //   },
    //   {
    //     title: 'USA Rider',
    //     icon: mdiBike,
    //     to: routeNames.USAC_RIDER,
    //   },
    // ];
    const menuItems = ref([]);

    const onSessionExpired = () => {
      router.replace({name: routeNames.AUTH, query: {next: route.value.fullPath, ...route.query}});
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


    return {
      menuItems
    }
  },
}
</script>
