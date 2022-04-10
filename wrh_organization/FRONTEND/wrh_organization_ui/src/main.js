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
import "vue-toastification/dist/index.css";
import DatetimePicker from 'vuetify-datetime-picker'

Vue.use(VueMask);
Vue.use(Toast, {
  transition: "Vue-Toastification__fade",
  maxToasts: 20,
  newestOnTop: true
});
Vue.use(DatetimePicker);

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
    axios.get("account/session").then(
      (response) => {
        store.state.currentUser = response.data;
      },
      (error) => {
        if (401 !== (error.response && error.response.status)) {
          alert(error);
        }
      }
    );
    // axios.get("bycing_org/member/me").then(
    //   (response) => {
    //     store.state.currentMember = response.data;
    //   },
    //   (error) => {
    //     if (401 !== (error.response && error.response.status)) {
    //       alert(error);
    //     }
    //   }
    // );
  }
}).$mount('#app');


/********************** public vars(mostly for testing shall be delete!) ************************/
window.Vue = Vue;
window.app = app;
window.router = router;
window.store = store;
window.utils = utils;
