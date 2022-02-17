import moment from "moment";


export const getQueryParams = (params, url) => {
  let href = url;
  let reg = new RegExp("[?&]" + params + "=([^&#]*)", "i");
  let queryString = reg.exec(href);
  return queryString ? queryString[1] : null;
};

export const getParameterByName = (name, url) => {
  name = name.replace(/[[]]/g, "\\$&");
  var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
      results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, " "));
};

export const addQSParm = (url, name, value, override) => {
  override = override === undefined ? true : override;
  if (value instanceof Array) {
    value.forEach(v => {
      url = addQSParm(url, name, v, false);
    })
    return url;
  }
  var re = new RegExp("([?&]" + name + "=)[^&]+", "");

  function add(sep) {
    url += sep + name + "=" + encodeURIComponent(value);
  }

  function change() {
    url = url.replace(re, "$1" + encodeURIComponent(value));
  }

  if (url.indexOf("?") === -1) {
    add("?");
  } else {
    if (override && re.test(url)) {
      change();
    } else {
      add("&");
    }
  }
  return url;
};

export const combineURLs = (baseURL, relativeURL) => {
  return (
      baseURL.replace(/\/+$/, "") + "/" + relativeURL.replace(/^\/+/, "")
  );
};

export const randomId = (n) => {
  n = n || 10;
  return Math.floor(Math.random() * Math.pow(10, n) + 1);
};

export const jsonParseSafe = (s, _default) => {
  try {
    return JSON.parse(s)
  } catch (e) {
    return _default;
  }
};

export const humanizeDate = (dt) => {
  if (!dt) {
      return;
  }
  dt = moment(dt);
  var now = moment(),
      format;
  if (now.year() === dt.year() && now.month() === dt.month() && now.date() === dt.date()) {
      format = 'h:mm a';
  } else if (now.year() === dt.year()) {
      format = 'MMM DD';
  } else {
      format = 'MMM D YYYY';
  }
  return dt.format(format)
};

export const formatDate = (value, fmt, _default) => {
  _default = _default === undefined ? "" : _default;
  if (!value) {
    return _default;
  }
  fmt = fmt === undefined ? "MMM D, YYYY HH:mm" : fmt;
  return moment(value).format(fmt);
};

export const formatTime = (value, fmt, _default) => {
  _default = _default === undefined ? "" : _default;
  if (!value) {
    return _default;
  }
  fmt = fmt === undefined ? "hh:mm A" : fmt;
  return moment.utc(`2000-01-01T${value}Z`).format(fmt);
};

