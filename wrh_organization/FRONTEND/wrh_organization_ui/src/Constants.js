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
