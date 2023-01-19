<template>
  <div class="gmap-container">
    <v-autocomplete
        v-if="!readonly"
        outlined
        dense
        v-model="address"
        :items="searchResult"
        clerable
        name="address"
        :search-input.sync="search"
        label="Locate Address"
        placeholder="Locate Address"
        autocomplete="off"
        item-text="formatted_address"
        return-object
        @change="selectAddress"
        hide-details
        class="mb-1"
    ></v-autocomplete>

    <GmapMap
        :center="{
        lat: latitude || 0,
        lng: longitude || 0,
      }"
        :zoom="7"
        :style="mapStyle"
    >
      <GmapMarker
          :position="{
          lat: latitude || 0,
          lng: longitude || 0,
        }"
          :draggable="!readonly"
          @dragend="location => updateCoordinates({lat: location.latLng.lat(), lng: location.latLng.lng()})"
      ></GmapMarker>
    </GmapMap>
  </div>
</template>

<script>
import geolocation from "vue-browser-geolocation";
import {onMounted, ref, watch, nextTick} from "@vue/composition-api";
import {notifyDefaultServerError} from "@/composables/utils";
import { helpers, getGoogleMapsAPI } from 'gmap-vue';
const { googleMapsApiInitializer } = helpers;
window.getGoogleMapsAPI = getGoogleMapsAPI;

export default {
  props: {
    latitude: {
      type: Number,
      default: 0
    },
    longitude: {
      type: Number,
      default: 0
    },
    readonly: {
      type: Boolean,
      default: false
    },
    apiKey: {
      type: String,
      required: true
    },
    mapStyle: {
      default: "width: auto; height: 360px"
    },
  },
  emits: {
    'update:latitude': null,
    'update:longitude': null,
  },
  setup(props, context) {
    const search = ref(null);
    const address = ref(null);
    const searchResult = ref([]);

    watch(search, val => {
      googleSearch(val)
    });

    onMounted(() => {
      googleMapsApiInitializer({
        key: props.apiKey,
        libraries: 'places'
      }, false);
      setTimeout(getCurrentLocation, 300)
    });

    const updateCoordinates = (location) => {
      context.emit('update:latitude', location.lat);
      context.emit('update:longitude', location.lng);
    };

    const getCurrentLocation = (force) => {
      if (props.readonly) {
        return;
      }
      if (!force && props.latitude && props.longitude) {
        return;
      }
      geolocation.getLocation({}).then((coordinates) => {
        updateCoordinates({lat: coordinates.lat, lng: coordinates.lng});
      })
    };

    const selectAddress = () => {
      if (!address.value) {
        return;
      }
      updateCoordinates({lat: address.value.geometry.location.lat, lng: address.value.geometry.location.lng});
      nextTick(()=> {
        address.value = null;
      })
    };

    const googleSearch = (value) => {
      if (!value) {
        return;
      }
      let url =
          "https://maps.googleapis.com/maps/api/geocode/json?key=" + props.apiKey + "&address=";
      fetch(url + value)
          .then((response) => response.json())
          .then((jsonResult) => {
            searchResult.value = jsonResult.results;
          })
          .catch((err) => {
            notifyDefaultServerError(err);
          });
    };


    return {
      search,
      address,
      searchResult,
      selectAddress,
      getCurrentLocation,
      updateCoordinates,
    }

  }

};
</script>

<style scoped>
  .gmap-container {
    border: 1px solid lightgray;
    padding: 10px;
    border-radius: 5px;

  }
</style>
