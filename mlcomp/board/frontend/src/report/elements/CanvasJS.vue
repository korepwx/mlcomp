<template>
  <div class="figure-wrapper">
    <figure class="report-canvasjs" v-if="title">
      <div class="figure-container">
        <div :id="containerId">Loading, please wait ...</div>
      </div>
      <figcaption>Figure: {{ title }}</figcaption>
    </figure>
    <div class="report-canvasjs" v-if="!title">
      <div class="figure-container">
        <div :id="containerId">Loading, please wait ...</div>
      </div>
    </div>
  </div>
</template>

<script>
  import $ from 'jquery';
  import { getJSON } from '../../lib/utils.js';
  import CanvasJS from '../../lib/canvasjs.js';

  export default {
    props: ['rootUrl', 'data'],

    computed: {
      title() {
        return this.data['title'];
      },

      containerId() {
        return this.data['container_id'];
      },

      dataUrl() {
        return this.rootUrl + this.data['data'].path;
      }
    },

    mounted() {
      const self = this;
      getJSON({
        url: self.dataUrl,
        success(chart) {
          try {
            // regularise the data (replace NaN with null)
            if (chart['data']) {
              for (const data of chart['data']) {
                const dataPoints = data['dataPoints'];
                if (dataPoints) {
                  for (const dataPoint of dataPoints) {
                    for (const key of Object.keys(dataPoint)) {
                      const val = dataPoint[key];
                      if (isNaN(val)) {
                        dataPoint[key] = null;
                      }
                    } // for (key)
                  } // for (dataPoint)
                } // if (dataPoints)
              } // for (data)
            }

            // set the default height for figure
            if (!chart['height']) {
              chart['height'] = 300;
            }

            // render the chart
            const chartObject = new CanvasJS.Chart(self.containerId, chart);
            chartObject.render();
            $('#' + self.containerId).parent().height(chart['height']);
          } catch (e) {
            console.log(e);
            $('#' + self.containerId).html('Failed to render figure: ' + e.message);
          }
        },
        error(e) {
          $('#' + self.containerId).html('Failed to load data: ' + e);
        }
      });
    },

    data() {
      return {};
    }
  }
</script>

<style lang="scss" scoped>
  .figure-wrapper {
    display: inline;
  }

  // apply to both situations
  .report-canvasjs {
    display: block;
    width: 100%;
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
