<template>
  <v-card>
    <v-card-title class="align-start">
      <span>5 Next Events</span>
    </v-card-title>
    <v-divider></v-divider>

    <v-card-text>
      <v-list class="pt-0">
        <template v-for="(event, index) in events">
          <v-list-item
            :key="`li-${event.id}`"
            :class="`d-flex px-0 ${index > 0 ? '':''}`"
          >
            <v-list-item-content>
              <v-list-item-title>
                <a class="text-decoration-none" href="javascript:">{{ event.name }}</a>
              </v-list-item-title>
              <v-list-item-subtitle>
                <v-icon size="14">
                  {{ icons.mdiMapMarker }}
                </v-icon>
                {{ event.country || '' }}{{ event.state? ` - ${event.state}`:'' }}{{event.city? ` - ${event.city}`:'' }}
              </v-list-item-subtitle>
            </v-list-item-content>
            <v-list-item-action>
              <v-list-item-action-text>
                {{ $utils.formatDate(event.start_date, 'MMM D, YYYY') }}
                <v-icon size="14">
                  {{ icons.mdiCalendarBlankOutline }}
                </v-icon>
              </v-list-item-action-text>
            </v-list-item-action>
          </v-list-item>
          <v-divider
            v-if="index < events.length - 1"
            :key="`d-${event.id}`"
          ></v-divider>
        </template>

        <v-list-item v-if="!events || !events.length" class="text-center">
          <v-list-item-title>No Event!</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script>
import { mdiCalendarBlankOutline, mdiDotsVertical, mdiMapMarker } from '@mdi/js'
import {notifyDefaultServerError, refineVTableOptions} from "@/composables/utils";
import axios from "@/axios";
import {onMounted, ref} from "@vue/composition-api";
import moment from "moment";

export default {
  setup() {
    const loading = ref(false);
    const events = ref([]);

    const loadEvents = () => {
      loading.value = true;
      var params = {
        start_date__gte: moment().format("YYYY-MM-DD"),
        page_size: 5,
        order_by: 'start_date,name'
      };
      axios.get(`bycing_org/event`, {params: params}).then((response) => {
        loading.value = false;
        events.value = response.data.results;
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true)
      });

    };

    onMounted(() => {
      loadEvents();
    });

    return {
      events,
      icons: {
        mdiDotsVertical,
        mdiCalendarBlankOutline,
        mdiMapMarker,
      },
    }
  },
}
</script>
