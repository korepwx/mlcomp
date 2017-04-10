<template>
  <div class="report-canvasjs">
    <div class="figure-wrapper">
      <div :id="container_id">Loading, please wait ...</div>
    </div>
    <div class="clear"></div>
    <figcaption v-if="title">Figure: {{ title }}</figcaption>
  </div>
</template>

<script>
  import $ from 'jquery';
  const CanvasJS = require('canvasjs/dist/canvasjs.js');

  export default {
    props: ['data'],

    computed: {
      title() {
        return this.data['title'];
      },

      container_id() {
        return this.data['container_id'];
      },

      data_url() {
        return this.data['data'].path;
      }
    },

    mounted() {
      const self = this;
      $.ajax({
        url: self.data_url,
        success(data) {
          try {
            if (!data['height']) {
              data['height'] = 300;
            }
            $(self.$el).children('.figure-wrapper').height(data['height']);
            const chart = new CanvasJS.Chart(self.container_id, data);
            chart.render();
          } catch (e) {
            console.log(e);
            $(self.$el).html('Failed to render figure: ' + e);
          }
        },
        error(e) {
          console.log(e);
          $(self.$el).html('Failed to load data: ' + e.statusText);
        }
      });
    },

    data() {
      return {};
    }
  }
</script>

<style lang="scss" scoped>
  .report-canvasjs {
    .figure-wrapper {
      width: 100%;
    }
    .clear {
      clear: both;
    }
    figcaption {
      width: 100%;
      text-align: center;
    }

    width: 100%;
    max-width: 600px;
    display: block;
  }
</style>
