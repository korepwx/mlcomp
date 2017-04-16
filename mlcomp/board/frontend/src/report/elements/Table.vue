<template>
  <div class="report-table">
    <div v-if="title" class="title">Table: {{ title }} </div>
    <table>
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
        return this.data['title'];
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
    margin-bottom: 0.5em;
    font-weight: 400;
    font-size: 1.5em;
    text-align: center;
    color: $title-color;
  }
  .report-table {
    max-width: 100%;
    margin: 1em auto;
    overflow: auto;

    table {
      border-collapse: separate;
      border-spacing: 1px;
      background: #fff;
      width: 100%;
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
</style>
