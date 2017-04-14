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
    display: block;
    width: 100%;
    background: #fff;
    margin: 0 auto;
    padding: 10px 17px;
    box-shadow: 2px 2px 3px -1px rgba(0,0,0,0.35);

    .title {
      color: $title-color;
      text-align: center;
      font-size: 2em;
      padding-bottom: 0.5em;
    }

    table {
      width: 100%;
      font-size: 1.2em;
      margin-bottom: 15px;
    }

    thead, tfoot {
      background: #d1c4e9;

      tr th {
        font-weight: bold;
        padding: 5px 10px;
      }
      tr th span {
        padding-right: 20px;
        background-repeat: no-repeat;
        background-position: 100% 100%;
      }

      tr th.headerSortUp, #keywords tr th.headerSortDown {
        background: #acc8dd;
      }
    }

    tbody {
      tr {
        color: #555;
      }
      tr td {
        text-align: center;
        padding: 15px 10px;
      }
      tr td.lalign {
        text-align: left;
      }
    }

    figcaption {
      width: 100%;
      text-align: center;
      margin-top: 5px;
    }

    width: 100%;
    display: block;
  }
</style>
