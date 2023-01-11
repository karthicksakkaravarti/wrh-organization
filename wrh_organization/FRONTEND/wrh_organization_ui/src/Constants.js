import {countries} from "@/composables/countries";

export const UI_VERSION_HEADER_NAME = "x-ui-version";

export const GENDER_OPTIONS = [
  { value: "m", title: "Male" },
  { value: "f", title: "Female" },
  { value: "o", title: "Other" },
  { value: "u", title: "Unknown" }
];
export const GENDER_MAP = {};
GENDER_OPTIONS.forEach(function(v) {
  GENDER_MAP[v.value] = v;
});

export const COUNTRY_OPTIONS = countries;
export const COUNTRY_MAP = {};
COUNTRY_OPTIONS.forEach(function(v) {
  COUNTRY_MAP[v.code] = v;
});

export const ORGANIZATION_TYPE_OPTIONS = [
  { value: "regional", title: "Regional", css: "success" },
  { value: "team", title: "Team", css: "primary" },
  { value: "advocacy_volunteer", title: "Advocacy, Volunteer", css: "info" },
];
export const ORGANIZATION_TYPE_MAP = {};
ORGANIZATION_TYPE_OPTIONS.forEach(function(v) {
  ORGANIZATION_TYPE_MAP[v.value] = v;
});

export const ORGANIZATION_MEMBERSHIP_PLAN_OPTIONS = [
  { value: "1week", title: "1 Week", days: 7 },
  { value: "1month", title: "1 Month", days: 30 },
  { value: "3month", title: "3 Months", days: 90 },
  { value: "6month", title: "6 Months", days: 180 },
  { value: "1year", title: "1 Year", days: 365 },
  { value: "2year", title: "2 Years", days: 730 },
];
export const ORGANIZATION_MEMBERSHIP_PLAN_MAP = {};
ORGANIZATION_MEMBERSHIP_PLAN_OPTIONS.forEach(function(v) {
  ORGANIZATION_MEMBERSHIP_PLAN_MAP[v.value] = v;
});

export const MEMBER_FIELDS_SCHEMA_TYPE_OPTIONS = [
  { value: "string", title: "String" },
  { value: "text", title: "Text" },
  { value: "integer", title: "Integer" },
  { value: "float", title: "Float" },
  { value: "number", title: "Number" },
  { value: "boolean", title: "Boolean" },
  { value: "percent", title: "Percent" },
  { value: "date", title: "Date" },
  { value: "time", title: "Time" },
  { value: "datetime", title: "Date/Time" },
];
export const MEMBER_FIELDS_SCHEMA_TYPE_MAP = {};
MEMBER_FIELDS_SCHEMA_TYPE_OPTIONS.forEach(function(v) {
  MEMBER_FIELDS_SCHEMA_TYPE_MAP[v.value] = v;
});

export const RACE_FINISH_STATUS_OPTIONS = [
  { value: "ok", title: "Finished", css: "success" },
  { value: "dns", title: "DNS", css: "warning" },
  { value: "dnf", title: "DNF", css: "error" },
];
export const RACE_FINISH_STATUS_MAP = {};
RACE_FINISH_STATUS_OPTIONS.forEach(function(v) {
  RACE_FINISH_STATUS_MAP[v.value] = v;
});


export const DEFAULT_TABLE_PER_PAGE_OPTIONS = [5, 10, 25, 50, 100, -1];

export const SOCIAL_ACCOUNTS = [
  {
    img: 'strava.png',
    name: 'strava',
    title: 'Strava',
  },
  {
    img: 'zwift.png',
    name: 'zwift',
    title: 'Zwift',
  },
  {
    img: 'zwiftpower.png',
    name: 'zwiftpower',
    title: 'Zwift Power',
  },
  {
    img: 'youtube.png',
    name: 'youtube',
    title: 'Youtube',
  },
  {
    img: 'instagram.png',
    name: 'instagram',
    title: 'Instagram',
  },
  {
    img: 'facebook.png',
    name: 'facebook',
    title: 'Facebook',
  },
];

export const CONNECTED_ACCOUNTS = [
  {
    img: 'google.png',
    name: 'google',
    title: 'Google',
    text: 'Calendar and contacts',
  },
  {
    img: 'zwift.png',
    name: 'zwift',
    title: 'Zwift',
    text: 'Zwift events, races and results',
  },
  {
    img: 'strava.png',
    name: 'strava',
    title: 'Strava',
    text: 'Strava events, races and results',
  },
];

// export const EVENT_TAGS_PREDEFINED = [
//   'bike tour', 'bmx freestyle', 'bmx race', 'bmx racing', 'camp', 'chariot race', 'clinic', 'club membership',
//   'criterium', 'cross country', 'cx race', 'cycling camp', 'cyclocross', 'cyclocross racing', 'derny race',
//   'downhill', 'dual slalom', 'elimination', 'enduro', 'fat bike', 'freestyle', 'fun rides', 'gran fondo', 'gravel',
//   'gravel grinder', 'handicap', 'hill climb', 'international omnium', 'italian pursuit', 'keirin', 'longest lap',
//   'madison', 'match sprint', 'miss n out', 'motorpaced scratch', 'mountain bike racing', 'mtb', 'mtb enduro',
//   'multisport', 'nebra', 'off road', 'omnium', 'other', 'point a lap', 'points race', 'pursuit', 'recreational',
//   'road', 'road race', 'road race or circuit race', 'road racing', 'scratch race', 'series', 'snowball',
//   'special event', 'stage race', 'team pursuit', 'team sprint', 'tempo', 'time trial', 'track', 'track racing',
//   'training rides', 'training series', 'trials', 'unknown distance', 'virtual', 'virtual challenge', 'virtual race',
//   'virtual road race', 'win n out'
// ];

export const EVENT_SOURCE_OPTIONS = [
  { value: "usac", title: "USAC", css: "success" },
  { value: "colorado", title: "Colorado", css: "warning" },
];
export const EVENT_SOURCE_MAP = {};
EVENT_SOURCE_OPTIONS.forEach(function(v) {
  EVENT_SOURCE_MAP[v.value] = v;
});

export const DEFAULT_CKEDITOR_CONFIG = {
  toolbar: {
    items: [
      'heading', '|',
      'bold', 'italic', 'link', 'bulletedList', 'numberedList', '|',
      'indent', 'outdent', '|',
      'blockQuote', 'insertTable', '|',
      'undo', 'redo'
    ],
  },
};
