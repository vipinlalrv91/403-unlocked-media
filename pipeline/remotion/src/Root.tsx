import React from 'react';
import {Composition} from 'remotion';
import {Story, Spec} from './Story';
const empty: Spec & {frames: number} = {bg: 'forest.jpg', seed: 1, fx: [], segs: [], amp: [], chars: [], delay: 0, frames: 60};
export const Root: React.FC = () => (
  <Composition id="Story" component={Story as any} fps={30} width={1080} height={1920} durationInFrames={60}
    defaultProps={empty as any}
    calculateMetadata={({props}) => ({durationInFrames: Math.max(1, (props as any).frames)})} />
);
