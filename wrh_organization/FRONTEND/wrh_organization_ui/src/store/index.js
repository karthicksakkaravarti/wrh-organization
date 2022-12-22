import appConfigStoreModule from '@core/@app-config/appConfigStoreModule'
import Vue from 'vue'
import Vuex from 'vuex'
import app from './app'
import EventBus from "@/EventBus";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    currentUser: {},
    currentMember: {},
    checkedAuthentication: false,
    sitePrefs: {},
  },
  mutations: {
    currentUser: function(state, user) {
      const oldState = state.currentUser;
      state.currentUser = user || {};
      if (state.currentUser.id) {
        EventBus.emit("user:login", state.currentUser);
      } else {
        EventBus.emit("user:logout", oldState);
      }
      EventBus.emit("user:change-state", {newUser: state.currentUser, oldUser: oldState});
    }
  },
  actions: {
  },
  getters: {
    isStaffUser: function (state) {
      return true === state.currentUser.is_staff;
    },
    isSuperUser: function (state) {
      return true === state.currentUser.is_superuser;
    },
    isStaffOrSuperUser: function (state) {
      return (
        true === (state.currentUser.is_staff || state.currentUser.is_superuser)
      );
    },
    isAuthenticated: function (state) {
      return !!state.currentUser.id;
    },
    userFullName: function (state) {
      var name = "";
      if (state.currentUser.id) {
        if (state.currentUser.first_name) {
          name = state.currentUser.first_name;
        }
        if (state.currentUser.last_name) {
          name += " " + state.currentUser.last_name;
        }
        name = name.trim();
        if (!name) {
          name = state.currentUser.username;
        }
      }
      return name;
    },
    userDisplayName: function (state) {
      if (state.currentUser.id) {
        var name = (state.currentUser.first_name || state.currentUser.username);
        return name.charAt(0).toUpperCase() + name.slice(1);
      }
      return "";
    },
    currentUserId: function (state) {
      return state.currentUser.id;
    },
    memberDisplayName: function (state) {
      if (state.currentMember.id) {
        var name = (state.currentMember.first_name || null);
        return name && (name.charAt(0).toUpperCase() + name.slice(1));
      }
      return "";
    },
    currentMemberId: function (state) {
      return state.currentMember.id;
    },
    defaultRegionalOrg: function (state) {
      return (state.currentUser.prefs || {}).default_regional_org || null;
    }
  },
  modules: {
    appConfig: appConfigStoreModule,
    app,
  },
})
