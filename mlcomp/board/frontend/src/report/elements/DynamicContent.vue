<template>
  <div class="report-dynamic-content" v-html="html" :id="elementId"></div>
</template>

<script>
  import $ from 'jquery';
  import { getJSON } from '../../lib/utils.js';

  export default {
    props: ['rootUrl', 'data'],

    computed: {
      html() {
        return this.data['html'] || "";
      },

      elementId() {
        return this.data['element_id'];
      },

      scriptUrl() {
        const o = this.data['script'];
        return o && (this.rootUrl + o.path);
      },

      dataUrl() {
        const o = this.data['data'];
        return o && (this.rootUrl + o.path);
      }
    },

    mounted() {
      const self = this;

      function getData() {
        getJSON({
          url: self.dataUrl,
          success(data) {
            $('#' + self.elementId).attr('dynamic-content-data', data);
            executeScript();
          },
          error(e) {
            $(self.$el).html('Failed to load data: ' + e);
          }
        })
      }

      function executeScript() {
        window.jQuery = $;
        $.getScript(self.scriptUrl).fail(function(jqxhr, settings, e) {
          console.log(e);
          $(self.$el).html('Failed to execute script: ' + e.statusText);
        });
      }

      if (self.scriptUrl) {
        if (self.dataUrl) {
          getData();
        } else {
          $('#' + self.elementId).attr('dynamic-content-data', null);
          executeScript();
        }
      }
    },

    data() {
      return {};
    }
  }
</script>

<style lang="scss" scoped>
  .report-dynamic-content {
    display: inline;
  }
</style>
