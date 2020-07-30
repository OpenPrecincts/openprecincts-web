import React from "react";
import ReactMapboxGl, { Layer, Popup, Source } from "react-mapbox-gl";
import StateBounds from "./state-bounds";
import ElectionTypes from './election-types';

function toFixed(value, precision) {
  var power = Math.pow(10, precision || 0);
  return String(Math.round(value * power) / power);
}

function numberWithCommas(x) {
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

const Map = ReactMapboxGl({
  accessToken:
    "pk.eyJ1Ijoib3BlbnByZWNpbmN0cyIsImEiOiJjanVqMHJtM3gwMXdyM3lzNmZkbmpxaXpwIn0.ZU772lvU-NeKNFAkukT6hw",
});

class ElectionResultPopup extends React.Component {
  render() {
    if (!this.props.coordinates) {
      return null;
    }

    return (
      <Popup
        anchor="bottom-left"
        coordinates={[this.props.coordinates.lng, this.props.coordinates.lat]}
      >
        <div className="precinct-name">{this.props.precinctName}</div>
        <div className="county-name">{this.props.countyName}</div>
        <table className="elec-table">
          <thead>
            <tr>
              <th className="cand">Candidate</th>
              <th className="votes">Votes</th>
              <th className="pct">%</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="cand">
                <span className="party-dem">&#9679;</span> {this.props.demName}{" "}
              </td>
              <td>{numberWithCommas(this.props.demValue)}</td>
              <td>
                {toFixed(
                  (100 * parseInt(this.props.demValue)) /
                    (parseInt(this.props.demValue) +
                      parseInt(this.props.repValue)),
                  1
                )}
              </td>
            </tr>
            <tr>
              <td className="cand">
                <span className="party-rep">&#9679;</span> {this.props.repName}
              </td>
              <td>{numberWithCommas(this.props.repValue)}</td>
              <td>
                {toFixed(
                  (100 * parseInt(this.props.repValue)) /
                    (parseInt(this.props.demValue) +
                      parseInt(this.props.repValue)),
                  1
                )}
              </td>
            </tr>
          </tbody>
        </table>
      </Popup>
    );
  }
}

export default class PrecinctMap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showCounties: true,
    };

    this.toggleCounties = this.toggleCounties.bind(this);
    this.onMouseMove = this.onMouseMove.bind(this);
    this.onMouseLeave = this.onMouseLeave.bind(this);
  }

  toggleCounties(e) {
    this.setState({ showCounties: !this.state.showCounties });
    e.preventDefault();
    e.stopPropagation();
  }

  onMouseMove(e) {
    if (!(this.props.demProperty in e.features[0].properties)) {
      console.warn(
        `demProperty "${this.props.demProperty}" is not in ${Object.keys(
          e.features[0].properties
        )}`
      );
      return;
    }
    if (!(this.props.repProperty in e.features[0].properties)) {
      console.warn(
        `repProperty "${this.props.repProperty}" is not in ${Object.keys(
          e.features[0].properties
        )}`
      );
      return;
    }
    // update popup
    this.setState({
      popupCoordinates: e.lngLat,
      demValue: e.features[0].properties[this.props.demProperty],
      repValue: e.features[0].properties[this.props.repProperty],
    });
  }

  onMouseLeave(e) {
    this.setState({
      popupCoordinates: null,
    });
  }

  render() {
    return (
      <div>
        <nav id="precinct-menu-left">
          <div className="field">
              Election
              <div className="control">
                  <div className="select">
                      <select onChange={this.props.handleSelectElection}>
                      {
                          this.props.elections.map((election, index) => {
                          return <option
                              key={index}>
                                  {`${election.year} ${ElectionTypes[election.officeType]}`}
                              </option>
                          })
                      }
                      </select>
                  </div>
              </div>
          </div>
          <div className="field">
            <button
              className={this.state.showCounties ? 'button is-normal' : 'button is-primary is-active'}
              onClick={this.toggleCounties}>
              {this.state.showCounties ? 'Hide Counties' : 'Show Counties'}
            </button>
          </div>
        </nav>
        <div id="precinct-map">
          <Map
            style="mapbox://styles/openprecincts/cjuj606800n6l1fpord7d5xy6"
            fitBounds={StateBounds[this.props.stateFromPath]}
            fitBoundsOptions={{ padding: 20, animate: false }}
          >
            <Source
              id="precincts"
              tileJsonSource={{
                type: "vector",
                url:
                  "mapbox://openprecincts." + this.props.mbtileName,
              }}
            />
            <Source
              id="counties"
              tileJsonSource={{
                type: "vector",
                url: "mapbox://openprecincts.us-counties",
              }}
            />
            // right now, using point labels for counties. at some point, it
            will be better to do dynamic labeling like:
            https://medium.com/@yixu0215/dynamic-label-placement-with-mapbox-gl-js-turf-polylabel-1f84f1d4bf6b
            <Source
              id="counties_label"
              tileJsonSource={{
                type: "vector",
                url: "mapbox://openprecincts.3ow64t0q",
              }}
            />
            {this.state.showCounties ? (
              <>
                <Layer
                  id="counties"
                  type="line"
                  sourceId="counties"
                  sourceLayer="us_counties"
                  paint={{
                    "line-color": "#777",
                    "line-width": 3,
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
                    "text-halo-color": "rgba(255, 255, 255, 0.7)",
                  }}
                  layout={{
                    "text-field": "{NAME}",
                    "text-size": 11,
                  }}
                  filter={["==", "STATEFP", this.props.fips]}
                />
              </>
            ) : (
              ""
            )}
            <Layer
              id="precincts"
              type="fill"
              sourceId="precincts"
              sourceLayer="precincts"
              onMouseMove={this.onMouseMove}
              onMouseLeave={this.onMouseLeave}
              paint={{
                "fill-outline-color": 'rgb(0,0,0)',
                // "fill-outline-color": [
                //   "case",
                //   ["boolean", ["feature-state", "hover"], false],
                //   "rgba(0,0,0,1)",
                //   "rgba(0,0,0,1)",
                // ], // if we want to change the width of the outline on hover, we will unfortunately have to make a separate type: 'line' layer
                "fill-color": [
                  "interpolate-lab", // perceptual color space interpolation
                  ["linear"],
                  [
                    "/",
                    ["to-number", ["get", this.props.demProperty]],
                    [
                      "+",
                      ["to-number", ["get", this.props.demProperty]],
                      ["to-number", ["get", this.props.repProperty]],
                    ],
                  ],
                  0,
                  "red",
                  0.5,
                  "white", // note that, unlike functions, the "stops" are flat, not wrapped in two-element arrays
                  1,
                  "blue",
                ],
                "fill-opacity": 0.5,
              }}
            />
            <ElectionResultPopup
              coordinates={this.state.popupCoordinates}
              precinctName="" // features[0].properties.precinct
              countyName="" // features[0].properties.locality
              demName={this.props.demName}
              repName={this.props.repName}
              demValue={this.state.demValue}
              repValue={this.state.repValue}
            />
          </Map>
        </div>
      </div>
    );
  }
}
