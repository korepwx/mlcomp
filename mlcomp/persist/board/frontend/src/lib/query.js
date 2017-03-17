/**
 * Filter the storage groups by given status and query.
 */
export function filterGroups(groups, { status, query }) {
  // if no status filter and no query filter, directly return the groups.
  if (!status && !query) {
    return groups;
  }

  // build the status filter
  const matchStatus = (function() {
    if (status == 'Active') {
      return function (g) {
        return !!g.active_count;
      };
    } else if (status == 'Completed') {
      return function (g) {
        return !g.active_count;
      };
    } else {
      if (status != 'All') {
        console.log('Unknown status ' + status);
      }
      return function (g) {
        return true;
      };
    }
  })();

  // build the query filter
  const matchQuery = function(g) {
    return true;
  };

  // now filter the result
  return groups.filter(function(g) {
    return matchStatus(g) && matchQuery(g);
  });
}
