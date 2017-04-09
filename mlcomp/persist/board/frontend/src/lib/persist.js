import { ALL_STATUS } from './api.js';
import store from 'store';

/** Make a config proxy from the specified object. */
function makeConfig(obj) {
  const ret = {};
  for (const key of Object.keys(obj)) {
    const defaultValue = obj[key];
    Object.defineProperty(ret, key, {
      get: () => {
        const ret = store.get(key);
        if (typeof ret === 'undefined')
          return defaultValue;
        return ret;
      },
      set: (value) => {
        store.set(key, value);
      }
    });
  }
  return ret;
} // makeConfig

class PersistStorage {
  constructor() {
    this._boardConfig = makeConfig({
      // Whether or not the side panel should be open by default?
      sidePanelOpen: true,

      // The query string on the storage groups
      queryString: '',

      // The status filter on the storage groups
      statusFilter: ALL_STATUS
    });
  }

  get boardConfig() { return this._boardConfig; }
}

const persist = new PersistStorage();
export default persist;
