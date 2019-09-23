import React from "react";
import ReactMapboxGl, { Layer, Feature, Source } from 'react-mapbox-gl';
import StateBounds from "./state-bounds";


const Map = ReactMapboxGl({
  accessToken: 'pk.eyJ1Ijoib3BlbnByZWNpbmN0cyIsImEiOiJjanVqMHJtM3gwMXdyM3lzNmZkbmpxaXpwIn0.ZU772lvU-NeKNFAkukT6hw'
});

export default class PrecinctMap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      demProperty: "G18DStSEN",
      repProperty: "G18RStSEN",
      showCounties: true,
    };

    this.toggleCounties = this.toggleCounties.bind(this);
  }

  toggleCounties(e) {
    console.log(e);
    this.setState({showCounties: !this.state.showCounties});
    e.preventDefault();
    e.stopPropagation();
  }

  render() {
    return <div>
      <nav id="precinct-menu">
        <a href="#" className="active" onClick={this.toggleCounties}>
            Counties
        </a>
      </nav>
      <div id='precinct-map'>
      <Map
      style='mapbox://styles/openprecincts/cjuj606800n6l1fpord7d5xy6'
      zoom={[6.5]}
      fitBounds={StateBounds[this.props.state]}
    >
      <Source
        id="precincts" 
        tileJsonSource={{ type: "vector", url: "mapbox://openprecincts." + this.props.state + "-precincts" }}
      />
      <Source
        id="counties" 
        tileJsonSource={{ type: "vector", url: "mapbox://openprecincts.us-counties" }}
      />

      // right now, using point labels for counties. at some point, it will be better to do dynamic labeling like: https://medium.com/@yixu0215/dynamic-label-placement-with-mapbox-gl-js-turf-polylabel-1f84f1d4bf6b
      <Source
        id="counties_label" 
        tileJsonSource={{ type: "vector", url: "mapbox://openprecincts.3ow64t0q" }}
      />
      {this.state.showCounties ? <>
        <Layer
        id="counties"
        type="line"
        sourceId="counties"
        sourceLayer="us_counties"
        paint={{
          "line-color": "#777",
          "line-width": 1
        }}
        filter={["==", "STATEFP", this.props.fips]}
        />
        <Layer
        id="counties_label"
        type="symbol"
        sourceId="counties_label"
        sourceLayer="us_county_labels-1d656t"
        paint={{
          "text-halo-width": 2,
          "text-halo-color": "rgba(255, 255, 255, 0.7)" 
        }}
        layout={{
          "text-field": "{NAME}",
          "text-size": 11,
        }}
        filter={["==", "STATEFP", this.props.fips]}
      />
      </>
      : ""
      }
      <Layer
        id="precincts"
        type="fill"
        sourceId="precincts"
        sourceLayer="precincts"
        paint={{
          'fill-outline-color': ["case",
            ["boolean", ["feature-state", "hover"], false],
            "rgba(0,0,0,1)",
            "rgba(0,0,0,0.0)"
          ], // if we want to change the width of the outline on hover, we will unfortunately have to make a separate type: 'line' layer
          'fill-color': [
            "interpolate-lab", // perceptual color space interpolation
            ['linear'],
            ['/', ["to-number", ["get", this.state.demProperty]],
              ['+', ["to-number", ["get", this.state.demProperty]],
                ["to-number", ["get", this.state.repProperty]]
              ] ], 0, "red",
          .5, "white", // note that, unlike functions, the "stops" are flat, not wrapped in two-element arrays
            1, "blue"
          ],
          'fill-opacity': .5,
        }}
      />
    </Map>
    </div>
  </div>
  }
}
