import {useCallback, useEffect, useMemo} from 'react';
import {browserHistory} from 'react-router';

import {GridColumnSortBy} from 'sentry/components/gridEditable';
import {useLocation} from 'sentry/utils/useLocation';

export function useSortableColumns<T extends string>(options: {
  defaultSort: GridColumnSortBy<T>;
  querystringKey: string;
  sortableColumns: readonly string[];
}) {
  const {sortableColumns, querystringKey, defaultSort} = options;
  const location = useLocation();
  const currentSort = useMemo<GridColumnSortBy<T>>(() => {
    let key = location.query?.[querystringKey] ?? '';

    const isDesc = key[0] === '-';
    if (isDesc) {
      key = key.slice(1);
    }

    if (!key || !sortableColumns.includes(key as T)) {
      return defaultSort;
    }

    return {
      key,
      order: isDesc ? 'desc' : 'asc',
    } as GridColumnSortBy<T>;
  }, [location.query, sortableColumns, defaultSort, querystringKey]);

  useEffect(() => {
    const removeListener = browserHistory.listenBefore((nextLocation, next) => {
      if (location.pathname === nextLocation.pathname) {
        next(nextLocation);
        return;
      }

      if (querystringKey in nextLocation.query) {
        delete nextLocation.query[querystringKey];
      }

      next(nextLocation);
    });

    return removeListener;
  });

  const generateSortLink = useCallback(
    (column: T) => {
      if (!sortableColumns.includes(column)) {
        return () => undefined;
      }
      if (!currentSort) {
        return () => ({
          ...location,
          query: {
            ...location.query,
            functionsSort: column,
          },
        });
      }

      const direction =
        currentSort.key !== column
          ? 'desc'
          : currentSort.order === 'desc'
          ? 'asc'
          : 'desc';

      return () => ({
        ...location,
        query: {
          ...location.query,
          functionsSort: `${direction === 'desc' ? '-' : ''}${column}`,
        },
      });
    },
    [location, currentSort, sortableColumns]
  );

  const sortCompareFn = useCallback(
    (a: Partial<Record<T, string | number>>, b: Partial<Record<T, string | number>>) => {
      const aValue = a[currentSort.key];
      const bValue = b[currentSort.key];
      if (!aValue || !bValue) {
        return 1;
      }

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        if (currentSort.order === 'asc') {
          return aValue - bValue;
        }
        return bValue - aValue;
      }

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        if (currentSort.order === 'asc') {
          return aValue.localeCompare(bValue);
        }
        return bValue.localeCompare(aValue);
      }
      return 1;
    },
    [currentSort]
  );

  return {
    currentSort,
    generateSortLink,
    sortCompareFn,
  };
}
