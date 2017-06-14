import { getJSON } from "./utils.js";

function normTimestamp(tm) {
  if (tm)
    tm = Math.round(tm * 1000);
  return tm;
}

/** All storage statuses */
export const ALL_STATUS = ['active', 'error', 'success'];

/**
 * Storage object.
 */
export class Storage {
  constructor(path, name, data) {
    const running_status = data['running_status'] || null;
    if (running_status) {
      for (const k of ['start_time', 'active_time']) {
        if (running_status[k]) {
          running_status[k] = normTimestamp(running_status[k]);
        }
      }
    }
    this.path = path;
    this.name = name;
    this.description = data['description'] || '';
    this.tags = data['tags'] || [];
    this.create_time = normTimestamp(data['create_time'] || 0);
    this.update_time = normTimestamp(data['update_time'] || 0);
    this.running_status = running_status;
    this.is_active = !!data['is_active'];
    this.has_error = !!data['has_error'];
  }

  get is_success() { return !this.is_active && !this.has_error; }

  /** Get the full, absolute path of this storage (typically used as keys). */
  get full_path() {
    return '/' + (this.path ? this.path + '/' + this.name : this.name);
  }

  /** Get the path segments (typically used as search tokens). */
  get path_segments() {
    return this.full_path.split('/').filter(s => !!s);
  }
}

/**
 * Group of storage instances.
 */
export class StorageGroup {
  constructor(path) {
    this.path = path;
    this.items = [];
    this.update_time = 0;
    this.active_count = 0;
    this.error_count = 0;
    this.success_count = 0;
  }

  push(storage) {
    this.items.push(storage);
    this.update_time = Math.max(this.update_time, storage.update_time);
    if (storage.is_active)
      this.active_count += 1;
    else if (storage.has_error)
      this.error_count += 1;
    else
      this.success_count += 1;
  }

  filterStorage(filter) {
    const g = new StorageGroup(this.path);
    for (const itm of this.items) {
      if (filter(itm)) {
        g.push(itm);
      }
    }
    return g;
  }
}

/**
 * Get storage groups.
 *
 * @param url The URL of the API endpoint.
 * @param success Callback that receives the data on success.
 * @param error Callback that receives the error message.
 * @returns A list of storage groups, sorted in reverse order of "create_time".
 */
export function getStorageGroups({ url, success, error }) {
  getJSON({
    url: url,
    cache: false,
    success(data) {
      if (success) {
        try {
          function dfs(groups, pa_path, parent) {
            if (parent) {
              for (const child of parent) {
                // If the node is a directory node
                if (Array.isArray(child[1])) {
                  const path_pfx = pa_path ? pa_path + '/' : '';
                  dfs(groups, path_pfx + child[0], child[1]);
                }

                // Otherwise if the node is a storage node
                else {
                  // construct the storage object
                  const name = child[0];
                  const data = child[1];
                  const storage = new Storage(pa_path, name, data);

                  // add to the group, and update group properties
                  if (!groups[pa_path]) {
                    groups[pa_path] = new StorageGroup(pa_path);
                  }
                  const group = groups[pa_path];
                  group.push(storage);
                }
              }
            }
            return groups;
          }

          function cmp_int(x, y) {
            return x - y;
          }

          function cmp_str(x, y) {
            return x > y ? 1 : (x < y ? -1 : 0);
          }

          const gathered = dfs({}, '', data);
          const groups = [];
          for (const key of Object.keys(gathered)) {
            groups.push(gathered[key]);
          }
          groups.sort(function (x, y) {
            return (-cmp_int(x.update_time, y.update_time)) || (cmp_str(x.path, y.path));
          });
          for (let i = 0; i < groups.length; ++i) {
            groups[i].items.sort(function (x, y) {
              return (-cmp_int(x.create_time, y.create_time)) || (cmp_str(x.name, y.name));
            });
          }
          success(groups);

        } catch (e) {
          console.log(e);
          if (error) error(e.message);
        } // try
      } // if (success)
    },
    error(e) {
      if (error) error(e);
    }
  });
}