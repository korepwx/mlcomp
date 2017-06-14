import Fuse from 'fuse.js';

// Functions to match a storage by status filters
const statusMatchers = {
  "active": (s) => s.is_active,
  "success": (s) => !(s.is_active || s.has_error),
  "error": (s) => !s.is_active && s.has_error,
  "active+error": (s) => s.is_active || s.has_error,
  "active+success": (s) => s.is_active || !s.has_error,
  "error+success": (s) => !s.is_active,
  "active+error+success": (s) => true
};

/**
 * Class to filter storage groups according to query and status filters.
 */
export class GroupFilter {
  constructor(groups) {
    this.groups = groups;
    if (groups && groups.length > 0) {
      // gather all storage and build the searcher
      const storageList = Array.concat(...groups.map(g => g.items));
      const options = {
        tokenize: true,
        threshold: 0.1,
        location: 0,
        distance: 10,
        maxPatternLength: 32,
        minMatchCharLength: 1,
        keys: [
          'name', 'path', 'full_path', 'path_segments', 'description',
          'tags', 'running_status.hostname'
        ]
      };
      this.searcher = new Fuse(storageList, options);
    } else {
      this.searcher = null;
    }
  }

  getFiltered({ status, query }) {
    const self = this;

    // if no group is set, return null
    if (!this.groups) {
      return null;
    }

    // if no filter applied, return the groups directly.
    if (!status && !query) {
      return this.groups;
    }

    // Find the storage which matches the status or query.

    // build the status matcher
    let statusMatcher = (s) => true;
    const statusMatcherKey = Array.isArray(status) ? Array.from(status).sort().join('+') : String(status);
    if (!statusMatchers[statusMatcherKey]) {
      console.error(`Ignored unknown status filters ${status}.`);
    } else {
      statusMatcher = statusMatchers[statusMatcherKey];
    }

    // build the query matcher
    const queryMatcher = (function() {
      const matchedStorageFullPath = new Set();
      if (!!query && self.searcher) {
        for (const s of self.searcher.search(query)) {
          matchedStorageFullPath.add(s.full_path);
        }
        return (s) => matchedStorageFullPath.has(s.full_path);
      } else {
        return (s) => true;
      }
    })();

    // finally, filter the groups
    const storageFilter = (s) => statusMatcher(s) && queryMatcher(s);
    return this.groups.map((g) => g.filterStorage(storageFilter)).filter(g => g.items.length > 0);
  }
}
