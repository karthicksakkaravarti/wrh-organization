<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="600px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">{{isEditMode? `Edit Race Series #${record.id}`: 'New Race Series'}}</span>
      </v-card-title>
      <v-form @submit.prevent="save">
        <v-card-text>
          <v-container>
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
          </v-container>
        </v-card-text>

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
  mdiClock
} from '@mdi/js'
import {ref, computed} from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";
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
    const record = ref({_events: null, _races: null, _categories: null});
    const saving = ref(false);
    const deleting = ref(false);
    const confirmDelete = ref(false);
    const isEditMode = computed(() => !!record.value.id);
    const races = ref([]);
    const categories = ref([]);
    const events = ref([]);
    const eventSearchInput = ref('');
    const findingEvents = ref(false);

    watch(eventSearchInput, () => {
      findEventsDebounce(eventSearchInput.value);
    });

    const findEvents = (search, ids) => {
      if (findingEvents.value) {
        return;
      }
      var params = {search: search};
      if (ids && ids.length) {
        params.id__in = ids.join();
      }
      findingEvents.value = true;
      axios.get("bycing_org/event/", {params: params}).then((response) => {
        findingEvents.value = false;
        events.value = response.data.results.concat(record.value._events || []);
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
        races.value = response.data.results.concat(record.value._races || []);
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
      record.value = Object.assign({_events: null, _races: null, _categories: null}, r);
      record.value._events = events.value = [...(record.value._events || [])]; // copy events
      record.value._races = races.value = [...(record.value._races || [])]; // copy races
      record.value._categories = categories.value = [...(record.value._categories || [])]; // copy categories
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
      icons: {
        mdiDelete,
        mdiAlert,
        mdiCalendar,
        mdiClock
      },
    }
  },
}
</script>
