import React from "react";
import { CalculateMetadataFunction, Composition } from "remotion";
import { Edit } from "./Edit";
import sample from "./sample-timeline.json";
import type { Timeline } from "./types";

const metadata =
  (vertical: boolean): CalculateMetadataFunction<Timeline> =>
  ({ props }) => ({
    fps: props.fps,
    durationInFrames: Math.ceil(props.durationSec * props.fps),
    width: vertical ? 1080 : props.width,
    height: vertical ? 1920 : props.height,
  });

export const Root: React.FC = () => (
  <>
    <Composition
      id="SignatureEdit"
      component={Edit}
      defaultProps={sample as Timeline}
      calculateMetadata={metadata(false)}
      durationInFrames={1}
      fps={30}
      width={1920}
      height={1080}
    />
    <Composition
      id="SignatureEditVertical"
      component={Edit}
      defaultProps={sample as Timeline}
      calculateMetadata={metadata(true)}
      durationInFrames={1}
      fps={30}
      width={1080}
      height={1920}
    />
  </>
);

