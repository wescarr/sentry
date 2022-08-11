import React from 'react';

import ScoreBar from 'sentry/components/scoreBar';
import CHART_PALETTE from 'sentry/constants/chartPalette';

interface Props {
  replay: undefined | {countErrors: number; duration: number; urls: string[]};
}

const palette = new Array(10).fill([CHART_PALETTE[0][0]]);

function replayHighlight({replay}: Props) {
  let score = 1;

  if (replay) {
    const {countErrors, duration, urls} = replay;
    const pagesVisited = urls.length;

    const pagesVisitedOverTime = pagesVisited / (duration || 1);

    score = (countErrors * 25 + pagesVisited * 5 + pagesVisitedOverTime) / 10;
    score = Math.floor(Math.min(10, Math.max(1, score)));
  }

  return <ScoreBar size={20} score={score} palette={palette} radius={0} />;
}

export default replayHighlight;
