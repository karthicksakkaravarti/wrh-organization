import '@/plugins/vue-composition-api'
import '@/styles/styles.scss'
import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import router from './router'
import store from './store'
import axios from "@/axios";
import EventBus from "./EventBus";
import * as Constants from "./Constants";
import {Config} from "@/Config";
import { version as AppVersion } from "../package.json";
import Toast from "vue-toastification";
import * as utils from "@/composables/utils"
import VueMask from 'v-mask'
import DatetimePicker from 'vuetify-datetime-picker'
import Rollbar from 'rollbar';
import {notifyDefaultServerError} from "@/composables/utils";
import VueGeolocation  from 'vue-browser-geolocation'
import GmapVue from 'gmap-vue'

import "vue-toastification/dist/index.css";
import "../public/css/ckeditor-content-styles.css"

Vue.use(VueMask);
Vue.use(Toast, {
  transition: "Vue-Toastification__fade",
  maxToasts: 20,
  newestOnTop: true
});
Vue.use(DatetimePicker);
Vue.use(VueGeolocation);
Vue.use(GmapVue, {
  load: {
    key: process.env.VUE_APP_GMAP_TOKEN,
    libraries: 'places'
  }
})
Vue.prototype.$rollbar = new Rollbar({
  // accessToken: '',
  captureUncaught: true,
  captureUnhandledRejections: true,
  // codeVersion: AppVersion,
  enabled: process.env.VUE_APP_ROLLBAR_ENABLED === 'true' || process.env.NODE_ENV === 'production',
  environment: process.env.NODE_ENV,
  payload: {
    // Add custom data to your events by adding custom key/value pairs like the one below
    framework: 'vuejs',
    person: {
      id: null,
      username: null,
    },
    client: {
      javascript: {
        code_version: AppVersion,
        source_map_enabled: true,
        guess_uncaught_frames: true,
      }
    }
  }
});

Vue.config.errorHandler = (err, vm, info) => {
  vm.$rollbar.error(err);
  throw err; // rethrow
};

Vue.config.productionTip = false;

Vue.prototype.$http = axios;
Vue.prototype.$eventsBus = EventBus;
Vue.prototype.$publicPath = process.env.BASE_URL;
Vue.prototype.$appVersion = AppVersion;
Vue.prototype.$const = Constants;
Vue.prototype.$conf = Config;
Vue.prototype.$utils = utils;

let app = new Vue({
  router,
  store,
  vuetify,
  render: h => h(App),
  created: () => {
    axios.get("cycling_org/global_pref").then(
      (response) => {
        store.state.sitePrefs = response.data;
        app.$rollbar.configure({
          accessToken: store.state.sitePrefs.rollbar_client__access_token,
          environment: store.state.sitePrefs.rollbar_client__environment,
          enabled: app.$rollbar.options.enabled? store.state.sitePrefs.rollbar_client__enabled: false,
        });
      }, (error) => {
        notifyDefaultServerError(error, true);
      }
    );
    EventBus.on("user:change-state", ({newUser, oldUser}) => {
      app.$rollbar.configure({
        payload: {
          person: {
            id: newUser.id || null,
            username: newUser.username || null,
          }
        }
      });
    });
  }
}).$mount('#app');


/********************** public vars(mostly for testing shall be delete!) ************************/
window.Vue = Vue;
window._appObjs = {
  app,
  router,
  store,
  utils,
  env: process.env,
};
