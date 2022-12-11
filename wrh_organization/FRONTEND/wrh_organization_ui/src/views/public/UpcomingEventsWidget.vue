<template>
  <v-card>
    <v-card-title class="align-start pb-3 pt-5">
      <span>Upcoming Events</span>
      <v-spacer></v-spacer>
      <v-btn text color="info" :to="{name: $rns.PUBLIC_EVENTS, query: {start_date__gte: today, organization: (apiParams || {}).organization}}" x-small>View All</v-btn>
    </v-card-title>
    <v-divider></v-divider>

    <v-card-text>
      <v-list class="pt-0">
        <template v-for="(event, index) in events">
          <v-list-item
            :key="`li-${event.id}`"
            :class="`d-flex px-0 ${index > 0 ? '':''}`"
            :to="{name: $rns.PUBLIC_EVENT_PROFILE, params: {record_id: event.id}}"
          >
            <v-avatar size="38" class="me-3">
              <v-img :src="event.logo || require('@/assets/images/misc/no-photo.png')"></v-img>
            </v-avatar>
            <v-list-item-content>
              <v-list-item-title>
                <a class="text-decoration-none" href="javascript:">{{ event.name }}</a>
              </v-list-item-title>
              <v-list-item-subtitle>
                <v-icon size="14">
                  {{ icons.mdiMapMarker }}
                </v-icon>
                {{ event.country || '' }}{{ event.state? `, ${event.state}`:'' }}{{event.city? `, ${event.city}`:'' }}
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
  props: {
    apiParams: {
      type: Object,
      required: false
    },
  },
  setup(props) {
    const loading = ref(false);
    const events = ref([]);
    const today = moment().format("YYYY-MM-DD");

    const loadEvents = () => {
      loading.value = true;
      const params =  Object.assign({
        start_date__gte: today,
        page_size: 5,
        order_by: 'start_date,name'
      }, props.apiParams);
      axios.get(`cycling_org/event`, {params: params}).then((response) => {
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
      today,
      icons: {
        mdiDotsVertical,
        mdiCalendarBlankOutline,
        mdiMapMarker,
      },
    }
  },
}
</script>
