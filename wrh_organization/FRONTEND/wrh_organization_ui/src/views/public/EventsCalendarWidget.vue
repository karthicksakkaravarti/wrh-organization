<template>
  <v-sheet class="rounded event-calendar-widget">
    <full-calendar ref="calendarRef" :options="calendarOptions">
      <template #eventContent="item">
        <v-tooltip bottom z-index="9999">
          <template v-slot:activator="{ on, attrs }" class="text-truncate">
            <div v-bind="attrs" v-on="on" class="fc-event-main text-truncate">
              <div class="fc-event-main-frame">
                <div class="fc-event-title-container">
                  <div class="fc-event-title fc-sticky">{{ item.event.title }}</div>
                </div>
              </div>
            </div>
          </template>
          <div>
            <div class="mb-1 font-weight-bold">{{ item.event.title}}</div>
            <div class="small mb-1 text-caption">
              <v-icon size="14" color="info">{{ icons.mdiMapMarker }}</v-icon>
              {{ item.event.extendedProps.record.country || '' }}{{ item.event.extendedProps.record.state? ` - ${item.event.extendedProps.record.state}`:'' }}{{item.event.extendedProps.record.city? ` - ${item.event.extendedProps.record.city}`:'' }}
            </div>
            <div class="small">
              <v-icon size="14" color="info">{{ icons.mdiCalendar }}</v-icon>
              {{ $utils.formatDate(item.event.start, 'MMM D, YYYY') }}{{ item.event.extendedProps.record.end_date? ` - ${$utils.formatDate(item.event.extendedProps.record.end_date, 'MMM D, YYYY')}`:'' }}
            </div>
            <div class="mt-3 mb-3">
              {{ item.event.extendedProps.record.description || '[No-Description]'}}
            </div>
          </div>
        </v-tooltip>
      </template>
    </full-calendar>
    <v-overlay :value="loading" :absolute="true" opacity="0.3">
      <v-progress-circular indeterminate></v-progress-circular>
    </v-overlay>

  </v-sheet>

</template>

<script>
import FullCalendar from "@fullcalendar/vue";
import dayGridPlugin from "@fullcalendar/daygrid";
import listPlugin from '@fullcalendar/list';
import {ref, onMounted} from "@vue/composition-api";
import {notifyDefaultServerError, formatDate} from "@/composables/utils";
import axios from "@/axios";
import { mdiMapMarker, mdiCalendar } from '@mdi/js'
import moment from "moment";

export default {
  components: {
    FullCalendar
  },
  setup() {
    const calendarRef = ref(null);
    const loading = ref(false);
    const suppressDatesSetEvent = ref(false);

    const onResizeWindow = () => {
      calendarRef.value.getApi().setOption('height', Math.max(window.innerHeight - 310, 500));
    };

    const loadEvents = (params) => {
      params = Object.assign({page_size: 0}, params);
      loading.value = true;
      axios.get("bycing_org/event/", {params: params}).then((response) => {
        loading.value = false;
        var events = response.data.results.map(r => {
          var end_date = r.end_date;
          if (end_date) {
            end_date = moment(end_date).add(1, 'days').format('YYYY-MM-DD')
          }
          return {
            id: r.id, title: r.name, start: r.start_date, end: end_date, className: "scheduled-event",
            // color: typeOption.color,
            // textColor: typeOption.textColor,
            record: r
          }
        });
        suppressDatesSetEvent.value = true;
        calendarOptions.value.events = events;
        setTimeout(onResizeWindow, 1);
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true)
      });
    };
    const refreshCalendar = (calendarView) => {
      var calView = (calendarView || calendarRef.value.getApi()).view;
      var minDate = formatDate(calView.activeStart, "YYYY-MM-DD"),
          maxDate = formatDate(calView.activeEnd, "YYYY-MM-DD");
      loadEvents({start_date__lte: maxDate, start_date__gte: minDate});
    };
    const onDatesSet = (calendarView) => {
      if (suppressDatesSetEvent.value) {
        suppressDatesSetEvent.value = false;
        return;
      }
      refreshCalendar(calendarView);
    };
    const calendarOptions = ref({
      plugins: [ dayGridPlugin, listPlugin ],
      // themeSystem: "bootstrap",
      headerToolbar: {
        right: 'prevYear,prev,today,next,nextYear',
        center: 'title',
        left: 'dayGridMonth,dayGridWeek,listMonth'
      },
      // headerToolbar: false,
      initialView: "dayGridMonth",
      datesSet: onDatesSet,
      // navLinkDayClick: this.calendarNavLinkDayClick,
      // eventClick: this.calendarEventClick,
      navLinks: true,
      editable: false,
      events: [
      ],
      height: '500px',
      dayMaxEventRows: true,
      windowResize: onResizeWindow,
      // eventDidMount: this.calendarEventRender,
      // windowResizeDelay: 300,
    });

    onMounted(() => {
      setTimeout(onResizeWindow, 100);
    });

    return {
      calendarRef,
      loading,
      calendarOptions,
      refreshCalendar,
      icons: {
        mdiMapMarker,
        mdiCalendar,
      }
    }
  },
}
</script>

<style>
  .fc .fc-list-sticky .fc-list-day > * {
    z-index: 10;
  }
  .event-calendar-widget {
    padding: 20px;
  }

</style>
