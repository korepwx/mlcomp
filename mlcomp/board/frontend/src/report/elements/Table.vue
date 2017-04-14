<template>
  <div class="components">
    <div v-if="title" class="title">Table: {{ title }} </div>
    <div class="report-table">
      <table id="keywords">
        <thead v-if="data['header']">
          <tr v-for="row in data['header']" :key="row['name_scope']">
            <th v-for="col in row['cells']" :key="col['name_scope']" :rowspan="col['rowspan']" :colspan="col['colspan']">
              <dispatch :data="col" :rootUrl="rootUrl" :level="level" :inline="true"></dispatch>
            </th>
          </tr>
        </thead>
        <tbody v-if="data['rows']">
          <tr v-for="row in data['rows']" :key="row['name_scope']">
            <td v-for="col in row['cells']" :key="col['name_scope']" :rowspan="col['rowspan']" :colspan="col['colspan']">
              <dispatch :data="col" :rootUrl="rootUrl" :level="level" :inline="true"></dispatch>
            </td>
          </tr>
        </tbody>
        <tfoot v-if="data['footer']">
          <tr v-for="row in data['footer']" :key="row['name_scope']">
            <th v-for="col in row['cells']" :key="col['name_scope']" :rowspan="col['rowspan']" :colspan="col['colspan']">
              <dispatch :data="col" :rootUrl="rootUrl" :level="level" :inline="true"></dispatch>
            </th>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>

<script>
  import Dispatch from './Dispatch.vue';

  export default {
    props: ['rootUrl', 'data', 'level'],

    components: {
      dispatch: Dispatch
    },

    computed: {
      title() {
        if (this.data['title'])
          return this.data['title'];
        else if (this.data['name'])
          return this.data['name'];
        else
          return null;
      },

      url() {
        return this.rootUrl + this.data['path'];
      }
    },

    data() {
      return {};
    }
  }
</script>

<style lang="scss" scoped>
  @import './settings.scss';

  .title {
    font-weight: 300;
    font-size: 2em;
    text-align: center;
    color: $title-color;
  }
  .component {
    line-height: 1.5em;
    margin: 0 auto;
    padding: 2em 0 3em;
    width: 90%;
    max-width: 1000px;
    overflow: hidden;
  }
  .component .filler {
    color: #d3d3d3;
  }
  .report-table {
    table {
        border-collapse: collapse;
        margin-bottom: 2em;
        width: 100%;
        background: #fff;
    }
    td, th {
        padding: 0.75em 1.5em;
        text-align: left;
    }
    th {
      background-color: #7e57c2;
      font-weight: bold;
      color: #fff;
      white-space: nowrap;
    }
    tbody th {
    	background-color: #2ea879;
    }
    tbody tr:nth-child(2n-1) {
      background-color: #f5f5f5;
    }
  }

  /* For appearance */
  .report-table {
  	overflow-x: auto;
  	overflow-y: hidden;
  	position: relative;
  	margin: 2em 0;
  	width: 100%;

    .sticky-thead, .sticky-col, .sticky-intersect {
    	opacity: 0;
    	position: absolute;
    	top: 0;
    	left: 0;
    	z-index: 50;
    	width: auto; /* Prevent table from stretching to full size */
    }
  	.sticky-thead {
  		box-shadow: 0 0.25em 0.1em -0.1em rgba(0,0,0,.125);
  		z-index: 100;
  		width: 100%; /* Force stretch */
  	}
    .sticky-intersect {
  		opacity: 1;
  		z-index: 150;

  	}
		.sticky-intersect th {
			background-color: #666;
			color: #eee;
		}
    td,
    th {
    	box-sizing: border-box;
    }

    /* Not needed for sticky header/column functionality */
    td.user-name {
    	text-transform: capitalize;
    }
    .overflow-y {
    	overflow-y: auto;
    	max-height: 50vh;
    }

    width: 100%;
    display: block;
  }
</style>
