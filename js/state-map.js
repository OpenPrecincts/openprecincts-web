import React from 'react'
import SVG from 'react-inlinesvg';

export default class StateMap extends React.Component {
  constructor (props) {
    super(props);
    this.colorMap = this.colorMap.bind(this);
  }

  colorMap() {
    for(var [state, color] of Object.entries(this.props.states)) {
      const el = document.getElementById(state + "___mapsvg");
      if(el) {
        el.style["fill"] = color;
      }
    }
  }

  render() {
    return (
      <div id="state-map">
        <SVG src="/static/img/usa_base.svg" uniqueHash="mapsvg" onLoad={this.colorMap}></SVG>
      </div>
    );
  }
}
