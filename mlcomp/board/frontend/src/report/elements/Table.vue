<template>
  <div class="report-table">
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
    <figcaption v-if="title">Table: {{ title }}</figcaption>
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

  .report-table {
    table {
      width: 100%;
    }
    table, th, td {
      border: 1px solid black;
      border-collapse: collapse;
    }
    th, td {
      padding: 5px;
      text-align: left;
    }
    figcaption {
      width: 100%;
      text-align: center;
      margin-top: 5px;
    }

    width: 100%;
    max-width: $figure-max-width;
    display: block;
  }
</style>
