<template>
  <div class="report-dynamic-content" v-html="html" :id="element_id"></div>
</template>

<script>
  import $ from 'jquery';

  export default {
    props: ['data'],

    computed: {
      html() {
        return this.data['html'] || "";
      },

      element_id() {
        return this.data['element_id'];
      },

      script_url() {
        const o = this.data['script'];
        return o && o.path;
      },

      data_url() {
        const o = this.data['data'];
        return o && o.path;
      }
    },

    mounted() {
      const self = this;

      function getData() {
        $.ajax({
          url: self.data_url,
          success(data) {
            $('#' + self.element_id).attr('dynamic-content-data', data);
            executeScript();
          },
          error(e) {
            console.log(e);
            $(self.$el).html('Failed to load data: ' + e.statusText);
          }
        })
      }

      function executeScript() {
        window.jQuery = $;
        $.getScript(self.script_url).fail(function(jqxhr, settings, e) {
          console.log(e);
          $(self.$el).html('Failed to execute script: ' + e.statusText);
        });
      }

      if (self.script_url) {
        if (self.data_url) {
          getData();
        } else {
          $('#' + self.element_id).attr('dynamic-content-data', null);
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
