import React from "react";
import SVG from "react-inlinesvg";

export default class StateMap extends React.Component {
  // statuses: {'good': {'name': 'Good State', 'fill': 'green'}, ...}
  // states: [{'NC': 'good'}, ...]
  // link_template: () => "/collect/${state}"

  constructor(props) {
    super(props);
    this.state = { activeMap: "grid" };
    this.colorMap = this.colorMap.bind(this);
  }

  colorMap() {
    for (var [state, status] of Object.entries(this.props.states)) {
      const el = document.getElementById(state + "___mapsvg");
      if (el) {
        el.style["fill"] = this.props.statuses[status].fill;
      }
    }
  }

  render() {
    var mapElement = null;
    if (this.state.activeMap === "grid") {
      const statuses = this.props.statuses;
      const link_template = this.props.link_template;
      mapElement = (
        <div className="state-grid">
          {Object.entries(this.props.states).map(function(e) {
            const [state, status] = e;
            return (
              <div
                key={state}
                className={"state-grid-box " + state}
                onClick={function() {
                  window.location = link_template(state);
                }}
                style={{ backgroundColor: statuses[status].fill }}
              >
                {state}
              </div>
            );
          })}
        </div>
      );
    } else {
      mapElement = (
        <SVG
          src="/static/img/usa_base.svg"
          uniqueHash="mapsvg"
          onLoad={this.colorMap}
        ></SVG>
      );
    }

    return (
      <div>
        <div className="columns">
          <div className="column is-three-quarters">
            <div className="tabs is-small">
              <ul>
                <li
                  className={this.state.activeMap === "grid" ? "is-active" : ""}
                >
                  <a onClick={() => this.setState({ activeMap: "grid" })}>
                    Grid
                  </a>
                </li>
                <li
                  className={this.state.activeMap === "map" ? "is-active" : ""}
                >
                  <a onClick={() => this.setState({ activeMap: "map" })}>Map</a>
                </li>
              </ul>
            </div>
            {mapElement}
          </div>
          <div className="column">
            <h4 className="title is-4">Key</h4>
            <table className="table">
              <tbody>
                {Object.values(this.props.statuses).map(st => (
                  <tr key={st.name}>
                    <td style={{ backgroundColor: st.fill }}>&nbsp;</td>
                    <td>{st.name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        <div>
          {this.state.activeMap === "grid" ? (
            ""
          ) : (
            <p className="is-pulled-right" style={{ fontSize: "70%" }}>
              State map is based on{" "}
              <a href="https://commons.wikimedia.org/wiki/File:Blank_USA,_w_territories.svg">
                this base map
              </a>
              , licensed under a{" "}
              <a href="https://creativecommons.org/licenses/by-sa/3.0/deed.en">
                CC-BY-SA 3.0 Unported License
              </a>
              .
            </p>
          )}
        </div>
      </div>
    );
  }
}
