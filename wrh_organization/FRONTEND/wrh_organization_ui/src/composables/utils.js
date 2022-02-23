import moment from "moment";
import { createToastInterface } from "vue-toastification";


export const toast = createToastInterface({
  transition: "Vue-Toastification__fade",
  maxToasts: 20,
  newestOnTop: true
});

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

export const closeAllNotify = () => {
  toast.clear();
};

export const notifyMessage = (msg, opts) => {
  opts = Object.assign({
    position: "top-center",
    timeout: 5000,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: true,
    closeButton: "button",
    icon: true,
    rtl: false
  },opts || {});
  toast(msg, opts);
};

export const notifySuccess = (msg, duration, opts) => {
  notifyMessage(msg, Object.assign({
    type: "success",
    timeout: duration !== undefined ? duration : 5000
  }, opts || {}));
};

export const notifyError = (msg, duration, opts) => {
  notifyMessage(msg, Object.assign({
    type: "error",
    timeout: duration !== undefined ? duration : 5000
  }, opts || {}));
};

export const notifyWarn = (msg, duration, opts) => {
  notifyMessage(msg, Object.assign({
    type: "warning",
    timeout: duration !== undefined ? duration : 5000
  }, opts || {}));
};

export const notifyInfo = (msg, duration, opts) => {
  notifyMessage(msg, Object.assign({
    type: "info",
    timeout: duration !== undefined ? duration : 5000
  }, opts || {}));
};

export const notifyDefaultServerSuccess = (response, duration) => {
  duration = duration !== undefined ? duration : 5000;
  var defaultMsg = "Operation done successfully";
  notifySuccess(response.statusText || defaultMsg, duration);
};

export const notifyDefaultServerError = (error, showDetail, duration, extra_message) => {
  var response = error.response || error.request;
  var msg;
  if (response.status === 401) {
    return;
  }
  if (response.status === 502) {
    msg = `<strong class="text-dark">Server Temporary Unavailable!</strong>&nbsp; Down for maintenance! We will be back shortly.`
    return notifyError(msg, duration || 0);
  }
  duration = duration !== undefined ? duration : 50000;
  showDetail = showDetail !== undefined ? showDetail : true;
  notifyError({
    render: (h) => {
      var els = [];
      if (!response || response.status <= 0) {
        els.push(h('strong', 'Server Connection Error'));
      } else {
        els.push(h('strong', `${response.status}: ${response.statusText} | `));
        var jData = safeFromJson(response.data);
        if (showDetail && jData) {
          els.push(h('p', prettifyError(response.data)));
        }
        if (extra_message) {
          els.push(h('p', extra_message));
        }
      }
      return h('div', els);
    }
  }, duration);
};

export const safeFromJson = (s, nullIfFail) => {
  if (typeof s === "object") {
    return s;
  }
  nullIfFail = nullIfFail === undefined;
  try {
    return JSON.parse(s);
  } catch (e) {
    return nullIfFail ? null : s;
  }

};

export const prettifyError = (data) => {
  return JSON.stringify(data)
    .replace(/\[|\]|\}|\{/g, "")
    .replace(/\\"/g, '"')
    .replace('"non_field_errors":', "");
};
