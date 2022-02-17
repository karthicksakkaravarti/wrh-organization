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

Vue.config.productionTip = false;

Vue.prototype.$http = axios;
Vue.prototype.$eventsBus = EventBus;
Vue.prototype.$publicPath = process.env.BASE_URL;
Vue.prototype.$appVersion = AppVersion;
Vue.prototype.$const = Constants;
Vue.prototype.$conf = Config;

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
  }
}).$mount('#app');


/********************** public vars ************************/
window.app = app;
window.router = router;
window.store = store;
