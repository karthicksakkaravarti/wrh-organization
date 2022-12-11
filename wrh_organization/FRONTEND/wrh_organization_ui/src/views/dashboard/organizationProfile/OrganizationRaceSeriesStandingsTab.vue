<template>
  <div class="organization-member-fields-tab">
    <v-card>
      <v-card-text class="d-flex align-center flex-wrap pb-0">
        <div class="d-flex align-center pb-5">
          <h2>Race-Series Standings Points</h2>
        </div>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-text class="pt-2 pb-2 pr-2 pl-2">
        <v-row>
          <v-col cols="12" md="6">
            <v-autocomplete
                v-model="selectedRaceSeries"
                outlined
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
                :disabled="!selectedRaceSeries"
                v-model="selectedCategory"
                outlined
                dense
                label="Choose a Category"
                :items="categories"
                item-text="title"
                item-value="id"
                :menu-props="{contentClass:'list-style'}"
                :loading="loadingCategories"
                no-data-text="No Category Found!"
                hide-details
                clearable
                return-object
            >
            </v-autocomplete>
          </v-col>

        </v-row>
      </v-card-text>
      <v-divider></v-divider>
      <v-simple-table>
        <template #default>
          <thead>
          <tr>
            <th class="">Place</th>
            <th class="">Points</th>
            <th class="">Rider</th>
            <th class="actions text-center">Actions</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="(r, idx) in records" :key="idx">
            <td class="">
              <span class="font-weight-semibold">{{ idx + 1 }}</span>
            </td>
            <td class="">
              <span class="font-weight-semibold">{{r.points}}</span>
            </td>
            <td class="">
              <div class="d-flex align-center">
                <v-avatar color="success" class="v-avatar-light-bg success--text" size="30">
                  <v-img v-if="r.rider.user && r.rider.user.avatar" :src="r.rider.user.avatar"></v-img>
                  <span v-else class="font-weight-medium">
                    {{ avatarText(r.rider.first_name || 'N/A') }}
                  </span>
                </v-avatar>

                <div class="d-flex flex-column pl-1">
                  <span href="javascript:" class="font-weight-semibold text-truncate text-decoration-none">
                    <v-icon v-if="r.rider.id" small>{{icons.mdiAccountCheck}}</v-icon> {{ r.rider.first_name }} {{ r.rider.last_name }}
                  </span>
                </div>
              </div>

            </td>
            <td class="actions text-center">
              <v-tooltip bottom>
                <template #activator="{ on, attrs }">
                  <v-btn v-on="on" v-bind="attrs" tabindex="-1" x-small
                         outlined class="mr-1">
                    Results
                  </v-btn>
                </template>
                <span>View Rece-Series Records</span>
              </v-tooltip>
            </td>
          </tr>
          <tr v-if="records.length == 0">
            <td colspan="5" class="text-center">
              No Record!
            </td>
          </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-card>
    <v-overlay :value="loading" :absolute="true" opacity="0.3">
      <v-progress-circular indeterminate></v-progress-circular>
    </v-overlay>
  </div>
</template>

<script>

import {notifyDefaultServerError} from "@/composables/utils";
import axios from "@/axios";
import {avatarText} from "@core/utils/filter";
import {ref} from "@vue/composition-api";
import {
  mdiPlusCircleOutline,
  mdiPlus,
  mdiCogOutline,
  mdiDelete,
  mdiArrowUpThin,
  mdiAccountCheck,
} from "@mdi/js"
import {watch} from "@vue/composition-api/dist/vue-composition-api";
import _ from "lodash";

export default {
  props: {
    organization: {
      type: Object,
      required: true
    },
  },
  components: {},
  setup(props, context) {
    const records = ref([]);
    const loading = ref(false);
    const selectedCategory = ref(null);
    const raceSeriesSearchInput = ref('');
    const selectedRaceSeries = ref(null);
    const findingRaceSeries = ref(false);
    const loadingCategories = ref(false);
    const raceSeries = ref([]);
    const categories = ref([]);

    watch(raceSeriesSearchInput, () => {
      findRaceSeriesDebounce(raceSeriesSearchInput.value);
    });
    watch(selectedRaceSeries, () => {
      loadRecords(1);
    });
    watch(selectedRaceSeries, () => {
      selectedCategory.value = null;
      loadCategories();
    });
    watch(selectedCategory, () => {
      loadRecords(1);
    });

    const loadCategories = () => {
      if (categories.value.length) {
        return
      }
      loadingCategories.value = true;
      var params = {organization: props.organization.id, page_size: 0, fields: 'id,title'};
      axios.get("cycling_org/category/", {params: params}).then((response) => {
        loadingCategories.value = false;
        categories.value = response.data.results;
      }, (error) => {
        loadingCategories.value = false;
        notifyDefaultServerError(error, true)
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

    const loadRecords = () => {
      if (!selectedRaceSeries.value || !selectedCategory.value) {
        records.value = [];
        return;
      }
      loading.value = true;
      var params = {organization: props.organization.id};
      axios.get(`cycling_org/race_series_result/standing_points/${selectedRaceSeries.value.id}/${selectedCategory.value.id}`,
          {params: params}).then((response) => {
        loading.value = false;
        records.value = response.data.results;
      }, (error) => {
        loading.value = false;
        notifyDefaultServerError(error, true);
      });

    };

    return {
      loading,
      records,
      loadRecords,
      selectedRaceSeries,
      selectedCategory,
      findRaceSeries,
      findRaceSeriesDebounce,
      findingRaceSeries,
      raceSeriesSearchInput,
      raceSeries,
      categories,
      loadingCategories,
      avatarText,
      icons: {
        mdiPlusCircleOutline,
        mdiPlus,
        mdiCogOutline,
        mdiDelete,
        mdiArrowUpThin,
        mdiAccountCheck,
      }
    }
  },
}
</script>

<style scoped>
  th.actions {
    min-width: 150px;
    width: 150px;
  }
</style>
