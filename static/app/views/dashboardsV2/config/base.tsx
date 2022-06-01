import {Series} from 'sentry/types/echarts';
import {TableData} from 'sentry/utils/discover/discoverQuery';

import {WidgetQuery} from '../types';

export default interface DatasetConfig<SeriesResponse, TableResponse> {
  /**
   * Transforms timeseries API results into series data that is
   * ingestable by echarts for timeseries visualizations.
   */
  transformSeries?: (data: SeriesResponse, widgetQuery: WidgetQuery) => Series[];
  /**
   * Transforms table API results into format that is used by
   * table and big number components
   */
  transformTable?: (data: TableResponse) => TableData;
}