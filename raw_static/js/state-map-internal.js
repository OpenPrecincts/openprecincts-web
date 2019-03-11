import React from 'react'
import SVG from 'react-inlinesvg';

export default class InteractiveMap extends React.Component {
  // statuses: {'good': {'name': 'Good State', 'fill': 'green'}, ...}
  // states: [{'NC': 'good'}, ...]
  // link_template: () => "/collect/${state}"
  
  constructor (props) {
    super(props);
  }

  render() {
    var mapElement = (
      <SVG src="/static/img/usa_base.svg" uniqueHash="mapsvg"></SVG>
    );

    return (
      <div>
        {mapElement}
      </div>
    );
  }
}
