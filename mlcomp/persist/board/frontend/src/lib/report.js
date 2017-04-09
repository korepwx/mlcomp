import $ from "jquery";

export function getReportObject({ url, success, error }) {
  $.ajax({
    url: url,
    success(data) {
      if (success) {
        success(data);
      }
    },
    error(e) {
      console.log(e);
      if (error) error(e.statusText);
    }
  })
}
