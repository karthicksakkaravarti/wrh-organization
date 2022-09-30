<template>
  <v-sheet class="rounded event-calendar-widget" :class="{'edit-mode': editMode}">
    <full-calendar ref="calendarRef" :options="calendarOptions">
      <template #eventContent="item">
        <v-tooltip bottom z-index="9999">
          <template v-slot:activator="{ on, attrs }" class="text-truncate">
            <div v-bind="attrs" v-on="on" class="fc-event-main text-truncate">
              <div class="fc-event-main-frame">
                <div class="fc-event-title-container">
                  <div class="fc-event-title fc-sticky">
                    <span v-if="item.event.extendedProps.record.source"
                          class="pa-1 mr-1 rounded-circle d-inline-block rounded-circle"
                          :class="($const.EVENT_SOURCE_MAP[item.event.extendedProps.record.source] || {}).css"></span>
                    {{ item.event.title }}</div>
                </div>
              </div>
            </div>
          </template>
          <div>
            <div class="mb-1 font-weight-bold">
              <span class="mr-1">{{ item.event.title}}</span>
              <v-chip x-small v-if="item.event.extendedProps.record.source" :color="($const.EVENT_SOURCE_MAP[item.event.extendedProps.record.source] || {}).css">
                {{($const.EVENT_SOURCE_MAP[item.event.extendedProps.record.source] || {}).title || item.event.extendedProps.record.source}}
              </v-chip>
            </div>
            <div class="small mb-1 text-caption">
              <v-icon size="14" color="info">{{ icons.mdiMapMarker }}</v-icon>
              {{ item.event.extendedProps.record.country || '' }}{{ item.event.extendedProps.record.state? `, ${item.event.extendedProps.record.state}`:'' }}{{item.event.extendedProps.record.city? `, ${item.event.extendedProps.record.city}`:'' }}
            </div>
            <div class="small mb-1">
              <v-icon size="14" color="info">{{ icons.mdiCalendar }}</v-icon>
              {{ $utils.formatDate(item.event.start, 'MMM D, YYYY') }}{{ item.event.extendedProps.record.end_date? ` - ${$utils.formatDate(item.event.extendedProps.record.end_date, 'MMM D, YYYY')}`:'' }}
            </div>
            <div class="small mb-1" v-if="item.event.extendedProps.record.organization">
              <v-icon size="14" color="info">{{ icons.mdiHomeOutline }}</v-icon>
              {{ item.event.extendedProps.record._organization.name }}
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
import {notifyDefaultServerError, formatDate, refineVTableOptions} from "@/composables/utils";
import axios from "@/axios";
import { mdiMapMarker, mdiCalendar, mdiHomeOutline } from '@mdi/js'
import moment from "moment";

export default {
  components: {
    FullCalendar
  },
  props: {
    apiParams: {
      type: Object,
      required: false
    },
    editMode: {
      type: Boolean,
      default: false
    },
  },
  setup(props, context) {
    const calendarRef = ref(null);
    const loading = ref(false);
    const suppressDatesSetEvent = ref(false);

    const refreshView = () => {
      calendarRef.value.getApi().setOption('height', Math.max(window.innerHeight - 310, 500));
    };

    const loadEvents = (params) => {
      params = Object.assign({page_size: 0}, props.apiParams, params);
      loading.value = true;
      axios.get("bycing_org/event/", {params: params}).then((response) => {
        loading.value = false;
        var events = response.data.results.map(r => {
          var end_date = r.end_date;
          if (end_date) {
            end_date = moment(end_date).add(1, 'days').format('YYYY-MM-DD')
          }
          return {
            id: r.id, title: r.name, start: r.start_date, end: end_date, className: "wrh-event",
            color: r.organization? 'green': null,
            // textColor: typeOption.textColor,
            record: r
          }
        });
        suppressDatesSetEvent.value = true;
        calendarOptions.value.events = events;
        setTimeout(refreshView, 1);
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
    const onCalendarNavLinkDayClick = (date, jsEvent) => {
      context.emit('nav-link-day-clicked', date)
    };
    const onEventClick = (info) => {
      context.emit('event-clicked', info.event.extendedProps.record)
    };

    const calendarOptions = ref({
      plugins: [ dayGridPlugin, listPlugin ],
      // themeSystem: "bootstrap",
      headerToolbar: {
        right: 'prevYear,prev,today,next,nextYear',
        center: 'title',
        left: 'dayGridMonth,dayGridWeek,dayGridDay,listMonth'
      },
      // headerToolbar: false,
      initialView: "dayGridMonth",
      datesSet: onDatesSet,
      navLinkDayClick: onCalendarNavLinkDayClick,
      eventClick: onEventClick,
      navLinks: props.editMode? true: false,
      navLinkHint: "Add New Event",
      editable: false,
      events: [
      ],
      height: '500px',
      dayMaxEventRows: true,
      windowResize: refreshView,
      // eventDidMount: this.calendarEventRender,
      // windowResizeDelay: 300,
    });

    onMounted(() => {
      setTimeout(refreshView, 100);
    });

    return {
      calendarRef,
      loading,
      calendarOptions,
      refreshCalendar,
      refreshView,
      icons: {
        mdiMapMarker,
        mdiCalendar,
        mdiHomeOutline,
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

  .event-calendar-widget.edit-mode a.fc-daygrid-day-number {
    text-decoration: none;
  }
  .event-calendar-widget.edit-mode .fc-daygrid-day-number::after {
    content: "";
    position: absolute;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%239155fd' d='M19 19V5H5V19H19M19 3A2 2 0 0 1 21 5V19A2 2 0 0 1 19 21H5A2 2 0 0 1 3 19V5C3 3.89 3.9 3 5 3H19M11 7H13V11H17V13H13V17H11V13H7V11H11V7Z' /%3E%3C/svg%3E") no-repeat;
    height: 16px;
    width: 16px;
    margin-left: -36px;
    margin-top: 4px;
    opacity: 0.5;
  }

  .event-calendar-widget .fc .fc-more-popover .fc-popover-body {
    max-height: 200px;
    overflow: auto;
  }

</style>
