<template>
  <v-dialog
    v-model="isVisible"
    persistent
    max-width="800px"
  >
    <v-card>
      <v-card-title>
        <span class="headline">Edit Race Series Results</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12">
              <div class="d-flex">
                <span class="mr-2">Race: </span>
                <div class="d-flex flex-column" v-if="race">
                  <span class="font-weight-semibold text-truncate">
                    {{race.name}}
                  </span>
                  <span class="text-xs text-truncate">
                    {{race._event.name}}
                  </span>
                </div>
              </div>
            </v-col>
            <v-col cols="12 pt-0">
              <v-divider></v-divider>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" md="6">
              <v-autocomplete
                  v-model="selectedRaceSeries"
                  dense
                  label="Choose a Race-Series"
                  :items="raceSeries"
                  item-text="name"
                  item-value="id"
                  hide-details
                  :search-input.sync="raceSeriesSearchInput"
                  :loading="findingRaceSeries"
                  no-data-text="No Result Found! Type here to Search Race-Series"
                  :menu-props="{contentClass:'list-style'}"
                  return-object
                  clearable
              >
                <template #selection="data">
                  <span class="d-block font-weight-medium text-truncate">
                    {{ data.item.name }}
                  </span>
                </template>
                <template #item="data">
                  <v-list-item-content>
                    <v-list-item-title class="text-sm">
                      {{ data.item.name }}
                    </v-list-item-title>
                    <v-list-item-subtitle>
                      <v-chip x-small v-for="e in (data.item._events || [])" :key="e.id" class="mr-1">
                        {{e.name}}
                      </v-chip>
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </template>
              </v-autocomplete>
            </v-col>

            <v-col cols="12" md="6">
              <v-autocomplete
                  v-model="category"
                  dense
                  label="Choose a Category"
                  :items="categories"
                  item-text="title"
                  item-value="id"
                  return-object
              >
              </v-autocomplete>
            </v-col>
          </v-row>
        </v-container>
        <v-simple-table :class="{disabled: !selectedRaceSeries || !category}">
          <template #default>
            <thead>
            <tr>
              <th class="">#</th>
              <th class="">Rider</th>
              <th class="">Place</th>
              <th class="">
                Category Place
                <v-btn outlined color="error" x-small @click="autoFillPlaces()">Auto Fill</v-btn>
              </th>
              <th class="actions text-center">Actions</th>
            </tr>
            </thead>
            <tbody>
            <tr v-for="(r, idx) in records" :key="idx">
              <td class="">
                <span>{{ r.id }}</span>
              </td>
              <td class="">
                <div class="d-flex align-center">
                  <v-avatar color="success" class="v-avatar-light-bg success--text" size="30">
                    <v-img v-if="r._rider && r._rider._user.avatar" :src="r._rider._user.avatar"></v-img>
                    <span v-else class="font-weight-medium">
                      {{ avatarText(r._rider? r._rider.first_name: (r.more_data.first_name || 'N/A')) }}
                    </span>
                  </v-avatar>

                  <div class="d-flex flex-column pl-1">
                    <span href="javascript:" class="font-weight-semibold text-truncate text-decoration-none">
                      <v-icon v-if="r._rider" small>{{icons.mdiAccountCheck}}</v-icon> {{ displayRiderName(r) }}
                    </span>
                  </div>
                </div>
              </td>
              <td class="">
                <span>{{r.place}}</span>
              </td>
              <td class="">
                <v-text-field type="number" min="1" step="1" v-model.number="raceSeriesResultPlaces[r.id]" dense single-line hide-details placeholder="Place">
                </v-text-field>
              </td>
              <td class="actions text-center">
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn v-on="on" v-bind="attrs" tabindex="-1" x-small
                           outlined class="mr-1" color="success" @click="save(r)" :loading="saving[r.id]"
                           :disabled="raceSeriesResultPlaces[r.id] == (raceSeriesResults[r.id] && raceSeriesResults[r.id].place)" >
                      Save
                    </v-btn>
                  </template>
                  <span>Save Catgory Place</span>
                </v-tooltip>
              </td>
            </tr>
            </tbody>
          </template>
        </v-simple-table>

      </v-card-text>

      <v-card-actions>
        <v-btn color="warning" @click="resetPlaces()">Reset</v-btn>
        <v-spacer></v-spacer>
        <v-btn color="secondary" outlined @click="hide()">Close</v-btn>
        <v-btn color="primary" :loading="savingAll" @click="saveAll()" :disabled="!notSavedRecords.length">Save All</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import {
  mdiDelete,
  mdiAlert,
} from '@mdi/js'
import {ref, computed, set} from '@vue/composition-api'
import axios from "@/axios";
import {notifyDefaultServerError, notifySuccess} from "@/composables/utils";
import {watch} from "@vue/composition-api/dist/vue-composition-api";
import _ from "lodash";
import {avatarText} from "@core/utils/filter";

export default {
  props: {
    organization: {
      type: Object,
      required: true
    }
  },
  setup(props, context) {
    const isVisible = ref(false);
    const race = ref(null);
    const selectedRaceSeries = ref(null);
    const category = ref(null);
    const saving = ref({});
    const savingAll = ref(false);
    const categories = ref([]);
    const raceSeries = ref([]);
    const raceSeriesResults = ref({});
    const raceSeriesResultPlaces = ref({});
    const records = ref([]);
    const recordsOrig = ref([]);
    const raceSeriesSearchInput = ref('');
    const findingRaceSeries = ref(false);

    watch(raceSeriesSearchInput, () => {
      findRaceSeriesDebounce(raceSeriesSearchInput.value);
    });
    watch(selectedRaceSeries, () => {
      loadRaceSeriesResults();
    });
    watch(category, () => {
      loadRaceSeriesResults();
    });

    const notSavedRecords = computed(() => {
      return records.value.filter(r => {
        return raceSeriesResultPlaces.value[r.id] !== (raceSeriesResults.value[r.id] && raceSeriesResults.value[r.id].place);
      })
    });

    const autoFillPlaces = () => {
      records.value.forEach((r, idx) => {
        // raceSeriesResultPlaces.value[r.id] = idx + 1;
        set(raceSeriesResultPlaces.value, r.id, idx + 1);
      });
    };

    const findRaceSeries = (search) => {
      if (findingRaceSeries.value) {
        raceSeries.value = [];
        return;
      }
      findingRaceSeries.value = true;
      axios.get("cycling_org/race_series/", {params: {search: search}}).then((response) => {
        findingRaceSeries.value = false;
        raceSeries.value = response.data.results;
      }, (error) => {
        findingRaceSeries.value = false;
        notifyDefaultServerError(error, true)
      });
    };

    const findRaceSeriesDebounce = _.debounce(findRaceSeries, 500);

    const loadCategories = () => {
      var params = {
        organization: props.organization.id,
        page_size: 0
      };
      axios.get("cycling_org/category/", {params: params}).then((response) => {
        categories.value = response.data.results;
      }, (error) => {
        notifyDefaultServerError(error, true)
      });
    };

    const loadRaceSeriesResults = () => {
      if (!selectedRaceSeries.value || !category.value) {
        return;
      }
      var params = {
        organization: props.organization.id,
        category: category.value.id,
        race: race.value.id,
        race_series: selectedRaceSeries.value.id,
        fields: 'id,race_result,place',
        page_size: 0
      };
      axios.get("cycling_org/race_series_result/", {params: params}).then((response) => {
        var results = {},
            places = {};
        response.data.results.forEach(r => {
          places[r.race_result] = r.place;
          results[r.race_result] = r;
        });
        raceSeriesResultPlaces.value = places;
        raceSeriesResults.value = results;
      }, (error) => {
        notifyDefaultServerError(error, true)
      });
    };

    const displayRiderName = (r) => {
      var name = '';
      if (r._rider) {
        name = `${r._rider.first_name} ${r._rider.last_name}`.trim();
      } else {
        name = `${r.more_data.first_name || ''} ${r.more_data.last_name || ''}`.trim();
      }
      return name || 'N/A'
    };

    const saveAll = () => {
      savingAll.value = true;
      Promise.all(notSavedRecords.value.map((r) => save(r, true))).finally(() => {
        savingAll.value = false;
        notifySuccess('Saved All.');
      });
    };

    const save = (r, ignoreSuccessNotify) => {
      var rid = raceSeriesResults.value[r.id]? raceSeriesResults.value[r.id].id: null;
      var data = {};
      var url = "cycling_org/race_series_result",
          httpMethod = axios.post,
          successMsg = "Race Series Result updated successfully.";
      if (rid) {
        url = `cycling_org/race_series_result/${rid}`;
        httpMethod = axios.patch;
      } else {
        data.organization = props.organization.id;
        data.race_result = r.id;
      }
      data.category = category.value.id;
      data.race_series = selectedRaceSeries.value.id;
      data.place = raceSeriesResultPlaces.value[r.id];
      set(saving.value, r.id, true);
      httpMethod(url, data).then((response) => {
        set(saving.value, r.id, false);
        raceSeriesResults.value[r.id] = response.data;
        !ignoreSuccessNotify && notifySuccess(successMsg, 2000);
        context.emit('save-successed', response.data);
      }, (error) => {
        set(saving.value, r.id, false);
        notifyDefaultServerError(error, true);
      });
    };

    const resetPlaces = () => {
      records.value = _.sortBy(recordsOrig.value.map(r => Object.assign({}, r)), ['place', 'id']);
      raceSeriesResultPlaces.value = {};
      raceSeriesResults.value = {};
      loadRaceSeriesResults();
      loadCategories();
    };

    const hide = () => {
      isVisible.value = false;
    };
    const show = (_race, _records) => {
      race.value = _race;
      recordsOrig.value = _records;
      records.value = _.sortBy(_records.map(r => Object.assign({}, r)), ['place', 'id']);
      raceSeriesResultPlaces.value = {};
      raceSeriesResults.value = {};
      selectedRaceSeries.value = null;
      category.value = null;
      saving.value = {};
      isVisible.value = true;
      loadCategories();
    };

    return {
      isVisible,
      raceSeriesSearchInput,
      raceSeries,
      raceSeriesResults,
      raceSeriesResultPlaces,
      selectedRaceSeries,
      findRaceSeries,
      findRaceSeriesDebounce,
      findingRaceSeries,
      saving,
      savingAll,
      categories,
      records,
      recordsOrig,
      hide,
      show,
      save,
      saveAll,
      avatarText,
      category,
      race,
      displayRiderName,
      autoFillPlaces,
      notSavedRecords,
      resetPlaces,
      icons: {
        mdiDelete,
        mdiAlert,
      },
    }
  },
}
</script>
<style>
  .v-data-table.disabled table {
    opacity: 0.7;
    pointer-events: none;
  }
</style>
