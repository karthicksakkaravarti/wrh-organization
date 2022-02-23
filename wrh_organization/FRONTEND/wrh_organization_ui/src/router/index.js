import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter);

export const routeNames = {
  ROOT: "root",
  ERROR_404: "error_404",

  PUBLIC_ROOT: "public_root",

  PUBLIC_HOME: "public_home",
  DASHBOARD_HOME: "dashboard_home",
  DASHBOARD_EVENTS: "dashboard_events",
  DASHBOARD_CLUB: "dashboard_club",
  DASHBOARD_RIDER: "dashboard_rider",
  DASHBOARD_ACCOUNT_SETTINGS: "dashboard_account_settings",
  DASHBOARD_USER_PROFILE: "dashboard_user_profile",

};

Vue.prototype.$rns = routeNames;

const routes = [
  {
    path: '/',
    name: routeNames.ROOT,
    redirect: {name: routeNames.PUBLIC_HOME},
  },
  {
    path: '/home',
    name: routeNames.PUBLIC_HOME,
    component: () => import('@/views/public/PublicHome.vue'),
    meta: {
      layout: 'PublicLayout',
    },
  },
  {
    path: '/dashboard/home',
    name: routeNames.DASHBOARD_HOME,
    component: () => import('@/views/dashboard/DashboardHome.vue'),
    meta: {
      layout: 'DashboardLayout',
    },
  },
  {
    path: '/dashboard/account-settings',
    name: routeNames.DASHBOARD_ACCOUNT_SETTINGS,
    component: () => import('@/views/dashboard/accountSettings/AccountSettings.vue'),
    meta: {
      layout: 'DashboardLayout',
    },
  },
  {
    path: '/dashboard/events',
    name: routeNames.DASHBOARD_EVENTS,
    component: () => import('@/views/dashboard/DashboardEvents.vue'),
    meta: {
      layout: 'DashboardLayout',
    },
  },
  {
    path: '/dashboard/club',
    name: routeNames.DASHBOARD_CLUB,
    component: () => import('@/views/dashboard/DasgboardClub.vue'),
    meta: {
      layout: 'DashboardLayout',
    },
  },
  {
    path: '/dashboard/rider',
    name: routeNames.DASHBOARD_RIDER,
    component: () => import('@/views/dashboard/DashboardRider.vue'),
    meta: {
      layout: 'DashboardLayout',
    },
  },
  {
    path: '/error-404',
    name: routeNames.ERROR_404,
    component: () => import('@/views/Error404.vue'),
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

export default router
