import moment from 'moment';

/**
 * Format timestamp as human readable string.
 */
export function formatTime(timestamp) {
  const tm = moment(timestamp);
  const now = moment();
  const date_diff = tm.diff(now);
  if (tm.date() === now.date() && Math.abs(date_diff) < 86400000) {
    const duration = moment.duration(date_diff);
    return duration.humanize(true);
  }
    // return duration.humanize();
  return tm.format('LLL');
}
