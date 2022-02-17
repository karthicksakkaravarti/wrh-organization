import { mdiApps, mdiHomeOutline } from '@mdi/js'
import {routeNames} from "@/router";

export default [
  {
    title: 'Home',
    icon: mdiHomeOutline,
    to: routeNames.PUBLIC_HOME,
  },
  {
    title: 'Dashboard',
    icon: mdiApps,
    to: routeNames.DASHBOARD_HOME,
  },
]
