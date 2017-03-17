import $ from "jquery";

export default class APIClient {
  constructor(endpoint) {
    this._endpoint = endpoint;
  }

  /**
   * Get storage groups from API backend.
   *
   * @param success Callback that receives the data on success.
   * @param error Callback that receives the error message.
   * @returns A list of storage groups, sorted in reverse order of "create_time".
   */
  getStorageGroups({ success, error }) {
    $.ajax({
      url: this._endpoint + "/all",
      success(data) {
        if (!success) {
        } else {
          try {
            function norm_timestamp(owner, key) {
              if (owner[key]) {
                owner[key] = Math.round(owner[key] * 1000);
              }
            }

            function dfs(groups, pa_path, parent) {
              if (parent) {
                for (const child of parent) {
                  // If the node is a directory node
                  if (Array.isArray(child[1])) {
                    if (pa_path)
                      pa_path += '/';
                    dfs(groups, pa_path + child[0], child[1]);
                  }

                  // Otherwise if the node is a storage node
                  else {
                    // construct the storage object
                    const data = child[1];
                    norm_timestamp(data, 'create_time');
                    norm_timestamp(data, 'update_time');
                    if (data['running_status']) {
                      norm_timestamp(data['running_status'], 'create_time');
                      norm_timestamp(data['running_status'], 'active_time');
                    }
                    const storage = {
                      path: pa_path,
                      name: child[0],
                      description: data['description'] || '',
                      create_time: data['create_time'] || 0,
                      update_time: data['update_time'] || 0,
                      is_active: !!data['is_active'],
                      has_error: !!data['has_error'],
                      data: data,
                    };

                    // add to the group, and update group properties
                    if (!groups[pa_path]) {
                      groups[pa_path] = {
                        path: pa_path,
                        items: [],
                        update_time: 0,
                        active_count: 0,
                        error_count: 0,
                        success_count: 0,
                      };
                    }
                    const group = groups[pa_path];
                    group.items.push(storage);
                    group.update_time = Math.max(group.update_time, storage.update_time);
                    if (storage.is_active)
                      group.active_count += 1;
                    else if (storage.has_error)
                      group.error_count += 1;
                    else
                      group.success_count += 1;
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
        console.log(e);
        if (error) error(e.statusText);
      }
    });
  }
}
