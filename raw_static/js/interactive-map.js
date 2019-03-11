import React from 'react'
import SVG from 'react-inlinesvg';

export default class InteractiveMap extends React.Component {
  // statuses: {'good': {'name': 'Good State', 'fill': 'green'}, ...}
  // states: [{'NC': 'good'}, ...]
  // link_template: () => "/collect/${state}"
  
  constructor (props) {
    super(props);
    this.state = {'activeMap': 'grid'};
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
    var mapElement = (
      // <SVG src="/static/img/usa_base.svg" uniqueHash="mapsvg" onLoad={this.colorMap}></SVG>
      <SVG src="/static/img/CA.svg"></SVG>
    );

    return (
      <div>
        {mapElement}
      </div>
    );
  }
}
