import React from 'react'
import SVG from 'react-inlinesvg';

export default class StateMap extends React.Component {
  // statuses: {'good': {'name': 'Good State', 'fill': 'green'}, ...}
  // states: [{'NC': 'good'}, ...]
  
  constructor (props) {
    super(props);
    this.colorMap = this.colorMap.bind(this);
  }

  colorMap() {
    for(var [state, status] of Object.entries(this.props.states)) {
      const el = document.getElementById(state + "___mapsvg");
      if(el) {
        el.style["fill"] = this.props.statuses[status].fill;
      }
    }
  }

  render() {
    return (
      <div>
      <div className="columns">
        <div className="column is-three-quarters">
          <SVG src="/static/img/usa_base.svg" uniqueHash="mapsvg" onLoad={this.colorMap}></SVG>
        </div>
        <div className="column">
            <h4 className="title is-4">Key</h4>
            <table className="table">
                <tbody>
                  { Object.values(this.props.statuses).map(st => (
                    <tr key={st.name}>
                      <td style={{"backgroundColor": st.fill}}>&nbsp;</td>
                      <td>{st.name}</td>
                    </tr>
                  )) }
                </tbody>
            </table>
        </div>
      </div>
      <div>
      <p className="is-pulled-right" style={{"fontSize": "70%"}}>State map is based on <a href="https://commons.wikimedia.org/wiki/File:Blank_USA,_w_territories.svg">this base map</a>, licensed under a <a href="https://creativecommons.org/licenses/by-sa/3.0/deed.en">CC-BY-SA 3.0 Unported License</a>.  </p>
      </div>
      </div>
    );
  }
}
