<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="700px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">{{isEditMode? `Edit Race Series #${record.id}`: 'New Race Series'}}</span>
      </v-card-title>
      <v-form @submit.prevent="save">
        <v-tabs class="mb-5">
          <v-tab>Basic Info</v-tab>
          <v-tab>Points Map</v-tab>
          <v-tab-item class="pt-6">
            <v-card-text>
              <v-row>
                <v-col cols="12">
                  <v-text-field v-model="record.name" label="Race Series Name" dense></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-autocomplete
                      v-model="record._events"
                      multiple
                      dense
                      label="Events"
                      :items="events"
                      item-text="name"
                      item-value="id"
                      hide-details
                      :search-input.sync="eventSearchInput"
                      :loading="findingEvents"
                      no-data-text="No Result Found! Type here to Search event"
                      :menu-props="{contentClass:'list-style'}"
                      return-object
                      clearable
                      class="pb-4"
                  >
                    <template #selection="data">
                      <v-chip small color="secondary" close @click:close="record._events.splice(data.index, 1)"
                              class="mt-1 mb-1">
                        {{ data.item.name }}
                      </v-chip>
                    </template>
                    <template #item="data">
                      <v-list-item-content>
                        <v-list-item-title class="text-sm">
                          {{ data.item.name }}
                        </v-list-item-title>
                        <v-list-item-subtitle>
                          {{ $utils.formatDate(data.item.start_date, 'MMM D, YYYY') }} - {{ $utils.formatDate(data.item.end_date, 'MMM D, YYYY') }}
                        </v-list-item-subtitle>
                      </v-list-item-content>
                    </template>
                    <template #prepend-item>
                      <v-row class="pl-1 pr-1 mb-1">
                        <v-col cols="12" md="6">
                          <v-menu v-model="eventFromDate" :close-on-content-click="false"
                              :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
                            <template v-slot:activator="{ on, attrs }">
                              <v-text-field class="pt-0 pb-0" v-model="eventFiltering.from_date" label="From Date" hide-details
                                            v-bind="attrs" v-on="on" dense readonly clearable filled>
                              </v-text-field>
                            </template>
                            <v-date-picker v-model="eventFiltering.from_date" color="primary" @input="eventFromDate = false">
                            </v-date-picker>
                          </v-menu>
                        </v-col>
                        <v-col cols="12" md="6">
                          <v-menu v-model="eventToDate" :close-on-content-click="false"
                              :nudge-right="40" transition="scale-transition" offset-y min-width="auto">
                            <template v-slot:activator="{ on, attrs }">
                              <v-text-field class="pt-0 pb-0" v-model="eventFiltering.to_date" label="To Date" hide-details
                                            v-bind="attrs" v-on="on" dense readonly clearable filled>
                              </v-text-field>
                            </template>
                            <v-date-picker v-model="eventFiltering.to_date" color="primary" @input="eventToDate = false">
                            </v-date-picker>
                          </v-menu>
                        </v-col>
                      </v-row>
                    </template>
                  </v-autocomplete>
                </v-col>
                <v-col cols="12">
                  <v-autocomplete
                      v-model="record._races"
                      multiple
                      dense
                      label="Races"
                      :items="races"
                      item-text="name"
                      item-value="id"
                      :menu-props="{contentClass:'list-style'}"
                      :disabled="!(record._events || []).length"
                      return-object
                  >
                    <template #selection="data">
                      <v-chip small color="primary" close @click:close="record._races.splice(data.index, 1)"
                              class="mt-1 mb-1">
                        {{ data.item.name }}
                      </v-chip>
                    </template>
                    <template #item="data">
                      <v-list-item-content>
                        <v-list-item-title class="text-sm">
                          {{ data.item.name }}
                        </v-list-item-title>
                        <v-list-item-subtitle>
                          {{ $utils.formatDate(data.item.start_datetime, 'MMM D, YYYY') }} - <small>{{data.item._event.name}}</small>
                        </v-list-item-subtitle>
                      </v-list-item-content>
                    </template>
                    <template #prepend-item>
                      <v-list-item>
                        <v-row align="center" justify="space-around">
                          <v-btn depressed @click="record._races=[...races]">
                            <v-icon>{{icons.mdiCheckboxMultipleMarkedOutline}}</v-icon> Select All
                          </v-btn>
                          <v-btn depressed @click="record._races=[]">
                            <v-icon>{{icons.mdiCheckboxMultipleBlankOutline}}</v-icon> Unselect All
                          </v-btn>
                        </v-row>
                      </v-list-item>
                    </template>
                  </v-autocomplete>
                </v-col>
                <v-col cols="12">
                  <v-autocomplete
                      v-model="record._categories"
                      multiple
                      dense
                      label="Categories"
                      :items="categories"
                      item-text="title"
                      item-value="id"
                      return-object
                  >
                    <template #selection="data">
                      <v-chip small color="info" close @click:close="record._categories.splice(data.index, 1)"
                              class="mt-1 mb-1">
                        {{ data.item.title }}
                      </v-chip>
                    </template>
                  </v-autocomplete>
                </v-col>

              </v-row>
            </v-card-text>
          </v-tab-item>
          <v-tab-item class="pt-6">
            <v-card-text>
              <v-alert border="left" color="primary" text dense>
                Enter Points of every place here!
              </v-alert>
              <v-row>
                <v-col cols="3" :key="`points-map-${p}`" v-for="p in pointsMapCount">
<!--                  <div class="font-weight-medium">#{{p}}:</div>-->
                  <v-text-field type="number" min="0" step="1" v-model.number="record.points_map[p]" outlined hide-details dense
                                :label="`Place #${p}`"></v-text-field>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="12">
                  <v-btn plain x-small color="primary" @click="pointsMapCount+=4">
                    <v-icon x-small>{{icons.mdiPlusCircleOutline}}</v-icon> Add More Places
                  </v-btn>
                </v-col>
              </v-row>

            </v-card-text>
          </v-tab-item>
        </v-tabs>
        <v-card-text v-if="confirmDelete">
          <v-alert type="warning" dense text :icon="icons.mdiAlert">
            <p>If you delete it, all related records will be deleted! Are you sure?</p>
            <v-btn color="error" outlined small :loading="deleting" @click="deleteRecord()">Yes, Delete It</v-btn>
            <v-btn color="secondary" @click="confirmDelete=false" small text class="ml-1">Cancel</v-btn>
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <template v-if="isEditMode" >
            <v-btn color="error" outlined @click="confirmDelete=true" :disabled="confirmDelete">
              <v-icon>{{icons.mdiDelete}}</v-icon>Delete
            </v-btn>
          </template>
          <v-spacer></v-spacer>
          <v-btn color="secondary" outlined @click="hide()">Close</v-btn>
          <v-btn color="primary" type="submit" :loading="saving">Save</v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script>
import {
  mdiDelete,
  mdiAlert,
  mdiCalendar,
  mdiClock,
  mdiCheckboxMultipleMarkedOutline,
  mdiCheckboxMultipleBlankOutline,
  mdiPlusCircleOutline,
} from '@mdi/js'
import {ref, computed} from '@vue/composition-api'
import axios from "@/axios";
import {formatDate, notifyDefaultServerError, notifySuccess} from "@/composables/utils";
import {watch} from "@vue/composition-api/dist/vue-composition-api";
import _ from "lodash";
import moment from "moment";

export default {
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  setup(props, context) {
    const isVisible = ref(false);
    const record = ref({_events: null, _races: null, _categories: null, points_map: {}});
    const saving = ref(false);
    const deleting = ref(false);
    const confirmDelete = ref(false);
    const isEditMode = computed(() => !!record.value.id);
    const races = ref([]);
    const categories = ref([]);
    const events = ref([]);
    const eventSearchInput = ref('');
    const findingEvents = ref(false);
    const eventFromDate = ref();
    const eventToDate = ref();
    const eventFiltering = ref({});
    const pointsMapCount = ref(20);

    watch(eventSearchInput, () => {
      findEventsDebounce(eventSearchInput.value);
    });

    watch(() => eventFiltering, (currentValue, oldValue) => {
        findEvents(eventSearchInput.value);
      },
      { deep: true }
    );

    const findEvents = (search, ids) => {
      if (findingEvents.value) {
        return;
      }
      var params = {search: search};
      if (ids && ids.length) {
        params.id__in = ids.join();
      }
      if (eventFiltering.value.from_date) {
        params.start_date__gte = eventFiltering.value.from_date
      }
      if (eventFiltering.value.to_date) {
        params.start_date__lte = eventFiltering.value.to_date
      }
      findingEvents.value = true;
      axios.get("bycing_org/event/", {params: params}).then((response) => {
        findingEvents.value = false;
        events.value = _.unionBy(response.data.results, record.value._events || [], r => r.id);
      }, (error) => {
        findingEvents.value = false;
        notifyDefaultServerError(error, true)
      });
    };

    const findEventsDebounce = _.debounce(findEvents, 500);

    const loadRaces = () => {
      if (!(record.value._events || []).length) {
        record.value._races = [];
        return;
      }
      var params = {
        event: record.value._events.map(r => r.id),
        page_size: 0
      };
      axios.get("bycing_org/race/", {params: params}).then((response) => {
        races.value = _.unionBy(response.data.results, record.value._races || [], r => r.id);
      }, (error) => {
        notifyDefaultServerError(error, true)
      });
    };

    watch(
        () => record.value._events,
        (current, old) => {
          loadRaces()
        },
        { deep: true }
    );

    const loadCategories = () => {
      var params = {
        organization: props.organization.id,
        page_size: 0
      };
      axios.get("bycing_org/category/", {params: params}).then((response) => {
        categories.value = response.data.results;
      }, (error) => {
        notifyDefaultServerError(error, true)
      });
    };

    const deleteRecord = () => {
      deleting.value = true;
      axios.delete(`bycing_org/race_series/${record.value.id}`).then((response) => {
        deleting.value = false;
        notifySuccess(`Race Series #${record.value.id} deleted.`);
        hide();
        context.emit('delete-successed', record.value);
      }, (error) => {
        deleting.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const save = () => {
      var data = Object.assign({}, record.value);
      var url = "bycing_org/race_series",
          httpMethod = axios.post,
          successMsg = "Race Series added successfully.";
      if (isEditMode.value) {
        url = `bycing_org/race_series/${record.value.id}`;
        httpMethod = axios.patch;
        successMsg = "Race Series updated successfully."
      } else {
        data.organization = props.organization.id;
      }
      data.events = data._events.map(r => r.id);
      data.races = data._races.map(r => r.id);
      data.categories = data._categories.map(r => r.id);
      delete data._events;
      delete data._races;
      delete data._categories;
      saving.value = true;
      httpMethod(url, data).then((response) => {
        saving.value = false;
        notifySuccess(successMsg);
        hide();
        context.emit('save-successed', response.data);
      }, (error) => {
        saving.value = false;
        notifyDefaultServerError(error, true);
      });
    };

    const hide = () => {
      isVisible.value = false;
    };
    const show = (r) => {
      record.value = Object.assign({_events: null, _races: null, _categories: null, points_map: {}}, r);
      record.value._events = events.value = [...(record.value._events || [])]; // copy events
      record.value._races = races.value = [...(record.value._races || [])]; // copy races
      record.value._categories = categories.value = [...(record.value._categories || [])]; // copy categories
      if (!record.value.points_map) {
        record.value.points_map = {};
      }
      pointsMapCount.value = _.max([_.maxBy(Object.keys(record.value.points_map), r => r * 1) * 1, 20]);
      confirmDelete.value = false;
      deleting.value = false;
      saving.value = false;
      if (record.value.events && record.value.events.length) {
        findEvents('', record.value.events);
      }
      loadCategories();
      isVisible.value = true;
    };

    return {
      isVisible,
      confirmDelete,
      isEditMode,
      record,
      saving,
      deleting,
      deleteRecord,
      hide,
      show,
      save,
      eventSearchInput,
      categories,
      races,
      events,
      findingEvents,
      findEvents,
      findEventsDebounce,
      eventFromDate,
      eventToDate,
      eventFiltering,
      pointsMapCount,
      icons: {
        mdiDelete,
        mdiAlert,
        mdiCalendar,
        mdiClock,
        mdiCheckboxMultipleMarkedOutline,
        mdiCheckboxMultipleBlankOutline,
        mdiPlusCircleOutline,
      },
    }
  },
}
</script>
