<template>
  <div class="figure-wrapper">
    <figure class="report-canvasjs" v-if="title">
      <div class="figure-container">
        <div :id="container_id">Loading, please wait ...</div>
      </div>
      <figcaption>Figure: {{ title }}</figcaption>
    </figure>
    <div class="report-canvasjs" v-if="!title">
      <div class="figure-container">
        <div :id="container_id">Loading, please wait ...</div>
      </div>
    </div>
  </div>
</template>

<script>
  import $ from 'jquery';
  const CanvasJS = require('canvasjs/dist/canvasjs.js');

  export default {
    props: ['root_url', 'data'],

    computed: {
      title() {
        return this.data['title'];
      },

      container_id() {
        return this.data['container_id'];
      },

      data_url() {
        return this.root_url + this.data['data'].path;
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
            const chart = new CanvasJS.Chart(self.container_id, data);
            chart.render();
            $('#' + self.container_id).parent().height(data['height']);
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
  @import './settings.scss';

  .figure-wrapper {
    display: inline;
  }

  // apply to both situations
  .report-canvasjs {
    display: block;
    width: 100%;
    max-width: $figure-max-width;
    border: 1px solid #ccc;
    border-radius: 2px;
    padding: 2px;
    margin: 1em 0;

    .figure-container {
      width: 100%;
    }
  }

  // apply only if the image is wrapped in figure
  .report-canvasjs {
    figcaption {
      width: 100%;
      text-align: center;
    }
  }
</style>
