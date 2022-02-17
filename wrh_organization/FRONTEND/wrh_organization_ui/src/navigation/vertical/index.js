import { mdiHomeOutline, mdiCalendarMultiselect, mdiAccountGroup , mdiBike} from '@mdi/js'
import {routeNames} from "@/router";

export default [
  {
    title: 'Home',
    icon: mdiHomeOutline,
    to: routeNames.DASHBOARD_HOME,
  },
  {
    title: 'USA Events',
    icon: mdiCalendarMultiselect,
    to: routeNames.DASHBOARD_EVENTS,
  },
  {
    title: 'USA Club',
    icon: mdiAccountGroup,
    to: routeNames.DASHBOARD_CLUB,
  },
  {
    title: 'USA Rider',
    icon: mdiBike,
    to: routeNames.DASHBOARD_RIDER,
  },
]
