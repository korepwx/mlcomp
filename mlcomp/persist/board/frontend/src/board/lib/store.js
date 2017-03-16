// Initialize Vuex
import Vue from 'vue';
import Vuex from 'vuex';
Vue.use(Vuex);

// Initialize the store
import APIClient from './api.js';
function getStore() {
  const apiClient = new APIClient('/_api');
  return new Vuex.Store({
    state: {
      system: window.__system__,
      isLoading: true,    // whether or not the storage directories are being loaded
      errorMessage: null, // message of the isLoading error
      storageGroups: null,  // the loaded storage directories
    },
    mutations: {
      setLoaded(state, { storageGroups, errorMessage }) {
        state.errorMessage = errorMessage;
        state.storageGroups = storageGroups;
        state.isLoading = false;
      }
    },
    actions: {
      loadStorageGroups({ commit }) {
        apiClient.getStorageGroups({
          success(data) {
            commit('setLoaded', { errorMessage: null, storageGroups: data });
          },
          error(e) {
            commit('setLoaded', { errorMessage: e, storageGroups: null });
          }
        })
      }
    }
  });
}

const store = getStore();
export default store;
