import $ from 'jquery';

/**
 * Check whether or not it is a desktop device.
 */
export function isDesktop() {
  return window.innerWidth > 993;
}

/**
 * Extended JSON parser which is able to parse "NaN", "Infinity".
 *
 * @param json The source of JSON.
 */
export function parseJSON(json) {
  /*return JSON.parse(json, (key, value) =>
    (
      (value === 'NaN') ? (NaN) : (
        (value === 'Infinity') ? (Infinity) : (
          (value === '-Infinity') ? (-Infinity) : (value)
        )
      )
    )
  );*/
  // fixme: use another method to parse JSON, instead of `eval()`
  return eval('(' + json + ')');
}

/**
 * Get JSON from API backend.
 *
 * @param url URL of the API backend.
 * @param success Callback on success.
 * @param error Callback on error.
 * @param cache Whether or not to use cache for this request? (default false)
 */
export function getJSON({ url, success, error, cache = false }) {
  $.ajax({
    url: url,
    success: function(data) {
      if (success) {
        try {
          success(parseJSON(data));
        } catch (e) {
          console.log(e);
          if (error) error(e.message);
        }
      }
    },
    error: function(e) {
      console.log(e);
      if (error) error(e.statusText);
    },
    cache: cache,
    dataType: 'text'
  })
}
