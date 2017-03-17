<template>
  <div>{{ text }}</div>
</template>

<script>
  import moment from 'moment';

  export default {
    props: {
      timestamp: {
        type: Number,
        default: 0
      }
    },

    data() {
      return {
        text: null,
      }
    },

    mounted() {
      this.hasDestroyed = false;
      this.updateInterval = null;
      this.updateIntervalSeconds = 0;
      this.updateText();
    },

    destroyed() {
      this.hasDestroyed = true;
      if (this.updateInterval) {
        clearInterval(this.updateInterval);
        this.updateInterval = null;
      }
    },

    methods: {
      updateText(timestamp=null) {
        console.log('updateText is called');
        const self = this;

        // get the time object
        const tm = moment(timestamp || self.timestamp);
        const now = moment();
        const date_diff = Math.floor(Math.abs(tm.diff(now)) / 1000);

        // get the desired refresh rate
        let refresh_rate = 0;
        let date_text = null;
        if (date_diff <= 61) {
          refresh_rate = 1;
        } else if (date_diff <= 3660) {
          refresh_rate = 60;
        } else if (date_diff <= 90000) {
          refresh_rate = 3600;
        } else {
          refresh_rate = null;
        }

        // get the date text
        if (date_diff < 60) {
          if (date_diff >= 2) {
            date_text = `${date_diff} seconds ago`;
          } else if (date_diff >= 1) {
            date_text = '1 second ago';
          } else {
            date_text = 'just now';
          }
        } else if (date_diff < 3600) {
          if (date_diff >= 120) {
            date_text = `${Math.floor(date_diff / 60)} minutes ago`;
          } else {
            date_text = '1 minute ago';
          }
        } else if (date_diff < 86400) {
          if (date_diff >= 7200) {
            date_text = `${Math.floor(date_diff / 3600)} hours ago`;
          } else {
            date_text = '1 hour ago';
          }
        } else {
          date_text = tm.format('LLL');
        }

        // update the date text
        self.text = date_text;

        // create the update updater if necessary
        if (!self.hasDestroyed /* component is not destroyed */) {
          if (!refresh_rate || refresh_rate != self.updateIntervalSeconds) {
            if (self.updateInterval) {
              clearInterval(self.updateInterval);
              self.updateInterval = null;
            }
          }
          if (refresh_rate && refresh_rate != self.updateIntervalSeconds) {
            self.updateInterval = setInterval(
              function() {
                self.updateText();
              },
              refresh_rate * 1000
            );
            self.updateIntervalSeconds = refresh_rate;
          }
        } // if (!hasDestroyed)
      }
    },

    watch: {
      timestamp : function (value) {
        this.updateText(value);
      }
    }
  }
</script>