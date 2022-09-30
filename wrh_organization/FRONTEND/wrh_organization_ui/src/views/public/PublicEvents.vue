<template>
  <v-card>
    <v-tabs v-model="tab" grow>
      <v-tab><v-icon>{{ icons.mdiTable }}</v-icon> Table</v-tab>
      <v-tab><v-icon>{{ icons.mdiCalendar }}</v-icon> Calendar</v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab" class="overflow-visible">
      <v-tab-item>
        <events-table-widget></events-table-widget>
      </v-tab-item>
      <v-tab-item>
        <events-calendar-widget></events-calendar-widget>
      </v-tab-item>
    </v-tabs-items>
  </v-card>
</template>

<script>
import {
  mdiCalendar,
  mdiTable,
} from '@mdi/js'
import EventsCalendarWidget from "@/views/public/EventsCalendarWidget";
import EventsTableWidget from "@/views/public/EventsTableWidget";
import {onMounted, ref} from "@vue/composition-api";
import {useRouter} from "@core/utils";
export default {
  components: {EventsTableWidget, EventsCalendarWidget},
  props: {
  },
  setup(props, context) {
    const { route } = useRouter();
    const tab = ref(null);

    onMounted(() => {
      var tabNumber = route.value.params.tab;
      if (tabNumber === undefined) {
        tabNumber = route.value.query.tab || undefined;
      }
      tab.value = tabNumber !== undefined? tabNumber * 1: 0 ;
    });

    return {
      tab,
      icons: {
        mdiCalendar,
        mdiTable,
      }
    }
  }
}
</script>
