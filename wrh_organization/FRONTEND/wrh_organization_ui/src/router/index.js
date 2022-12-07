import Vue from 'vue'
import VueRouter from 'vue-router'
import axios from "@/axios";
import store from "@/store";

Vue.use(VueRouter);

export const routeNames = {
  ROOT: "root",
  ERROR_404: "error_404",
  AUTH: "auth",

  PUBLIC_HOME: "public_home",
  PUBLIC_RACE_RESULTS: "public_race_results",
  PUBLIC_RIDER_PROFILE: "public_rider_profile",
  PUBLIC_ORG_PROFILE: "public_org_profile",
  PUBLIC_EVENT_PROFILE: "public_event_profile",
  PUBLIC_EVENTS: "public_events",

  WIDGET_ORG_PROFILE: "widget_org_profile",
  WIDGET_ORG_EVENTS_CALENDAR: "widget_org_events_calendar",
  WIDGET_RIDER_PROFILE: "widget_rider_profile",
  WIDGET_RACE_RESULTS: "widget_race_results",
  WIDGET_EVENTS_CALENDAR: "widget_events_calendar",

  USAC_EVENTS: "usac_events",
  USAC_CLUB: "usac_club",
  USAC_RIDER: "usac_rider",

  DASHBOARD_HOME: "dashboard_home",
  DASHBOARD_ACCOUNT_SETTINGS: "dashboard_account_settings",
  DASHBOARD_MEMBER_PROFILE: "dashboard_member_profile",
  DASHBOARD_ORGANIZATION_PROFILE: "dashboard_organization_profile",

};

Vue.prototype.$rns = routeNames;

const routes = [
  {
    path: '/',
    name: routeNames.ROOT,
    beforeEnter: (to, from, next) => {
      if (store.getters.defaultRegionalOrg) {
        next({name: routeNames.PUBLIC_ORG_PROFILE, params: {record_id: store.getters.defaultRegionalOrg}, query: to.query});
      } else {
        next({name: routeNames.PUBLIC_HOME, query: to.query});
      }
    },
  },
  {
    path: '/auth',
    name: routeNames.AUTH,
    component: () => import('@/views/auth/Auth'),
    meta: {
      layout: 'BlankLayout',
    },
    beforeEnter: (to, from, next) => {
      if (store.getters.isAuthenticated) {
        next({name: routeNames.ROOT, replace: true, query: to.query});
      } else {
        next();
      }
    },
  },
  {
    path: '/home',
    name: routeNames.PUBLIC_HOME,
    component: () => import('@/views/public/PublicHome'),
    meta: {
      layoutHideMenuItems: true
    },
  },
  {
    path: '/rider-profile/:record_id',
    name: routeNames.PUBLIC_RIDER_PROFILE,
    component: () => import('@/views/public/PublicRiderProfile'),
    meta: {
      layoutHideMenuItems: true
    },
  },
  {
    path: '/event-profile/:record_id',
    name: routeNames.PUBLIC_EVENT_PROFILE,
    component: () => import('@/views/public/PublicEventProfile'),
    meta: {
      layoutHideMenuItems: true
    },
  },
  {
    path: '/org-profile/:record_id',
    name: routeNames.PUBLIC_ORG_PROFILE,
    component: () => import('@/views/public/PublicOrgProfile'),
    meta: {
      layoutHideMenuItems: true
    },
  },
  {
    path: '/race-results',
    name: routeNames.PUBLIC_RACE_RESULTS,
    component: () => import('@/views/public/PublicRaceResults'),
    meta: {},
  },
  {
    path: '/events',
    name: routeNames.PUBLIC_EVENTS,
    component: () => import('@/views/public/PublicEvents'),
    meta: {},
  },
  {
    path: '/dashboard/home',
    name: routeNames.DASHBOARD_HOME,
    redirect: {name: routeNames.DASHBOARD_MEMBER_PROFILE}
    // component: () => import('@/views/dashboard/DashboardHome'),
    // meta: {
    //   layout: 'DashboardLayout',
    // },
  },
  {
    path: '/dashboard/account-settings',
    name: routeNames.DASHBOARD_ACCOUNT_SETTINGS,
    component: () => import('@/views/dashboard/accountSettings/AccountSettings'),
    meta: {
      layout: 'DashboardLayout',
    },
  },
  {
    path: '/dashboard/member-profile',
    name: routeNames.DASHBOARD_MEMBER_PROFILE,
    component: () => import('@/views/dashboard/memberProfile/MemberProfile'),
    meta: {
      layout: 'DashboardLayout',
    },
  },
  {
    path: '/dashboard/organization-profile/:record_id',
    name: routeNames.DASHBOARD_ORGANIZATION_PROFILE,
    component: () => import('@/views/dashboard/organizationProfile/OrganizationProfile'),
    meta: {
      layout: 'DashboardLayout',
    },
  },
  {
    path: '/usac/events',
    name: routeNames.USAC_EVENTS,
    component: () => import('@/views/dashboard/DashboardEvents'),
    meta: {},
  },
  {
    path: '/usac/club',
    name: routeNames.USAC_CLUB,
    component: () => import('@/views/dashboard/DashboardClub'),
    meta: {},
  },
  {
    path: '/usac/rider',
    name: routeNames.USAC_RIDER,
    component: () => import('@/views/dashboard/DashboardRider'),
    meta: {},
  },
  {
    path: '/widgets/org-profile/:record_id',
    name: routeNames.WIDGET_ORG_PROFILE,
    component: () => import('@/views/widgets/OrgProfileWidget'),
    meta: {
      layout: 'BlankLayout',
    },
  },
  {
    path: '/widgets/rider-profile/:record_id',
    name: routeNames.WIDGET_RIDER_PROFILE,
    component: () => import('@/views/widgets/RiderProfileWidget'),
    meta: {
      layout: 'BlankLayout',
    },
  },
  {
    path: '/widgets/race-results',
    name: routeNames.WIDGET_RACE_RESULTS,
    component: () => import('@/views/widgets/RaceResultsWidget'),
    meta: {
      layout: 'BlankLayout',
    },
  },
  {
    path: '/widgets/events-calendar',
    name: routeNames.WIDGET_EVENTS_CALENDAR,
    component: () => import('@/views/widgets/EventsCalendarWidget'),
    meta: {
      layout: 'BlankLayout',
    },
  },
  {
    path: '/widgets/events-calendar/:org_id',
    name: routeNames.WIDGET_ORG_EVENTS_CALENDAR,
    component: () => import('@/views/widgets/EventsCalendarWidget'),
    meta: {
      layout: 'BlankLayout',
    },
  },
  {
    path: '/error-404',
    name: routeNames.ERROR_404,
    component: () => import('@/views/Error404'),
    meta: {
      layout: 'BlankLayout',
    },
  },
  {
    path: '*',
    redirect: {name: routeNames.ERROR_404}
  },
];

const router = new VueRouter({
  base: process.env.BASE_URL,
  routes,
  scrollBehavior() {
    return { x: 0, y: 0 }
  },
});

router.afterEach((toRoute) => {
  let pageInfo = toRoute.meta.pageInfo || {},
      title = `WRH-Organization :: ${pageInfo.title || toRoute.name} ::`;
  if (pageInfo.titleDesc) {
    title = title + pageInfo.titleDesc;
  }
  window.document.title = title;
});

router.beforeEach((to, from, next) => {
  if (store.state.checkedAuthentication) {
    return next();
  }
  axios.get("account/session").then((response) => {
    store.state.currentUser = response.data;
  }, (error) => {
    if (401 !== (error.response && error.response.status)) {
      alert(error);
    }
  }).finally(() => {
    store.state.checkedAuthentication = true;
    next();
  });
});

export default router
