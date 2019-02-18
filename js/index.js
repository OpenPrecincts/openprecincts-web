import React from 'react'
import ReactDOM from 'react-dom'

import StateMap from './state-map'

function reveal() {
  document.querySelector(`[data-hidden=${this.dataset.reveal}]`).style.display = "block";
  this.style.display = "none";
}


window.addEventListener('load', () => {
  const sm = document.querySelector('[data-hook="state-map"]');
  const states = JSON.parse(document.getElementById('state-status').textContent);
  if (sm) {
    ReactDOM.render(React.createElement(
      StateMap,
      {
        states: states,
        statuses: {
          'unknown': {'name': 'Unknown', 'fill': '#999'},
          'waiting': {'name': 'External Partner', 'fill': 'orange'},
          'in-progress': {'name': 'Data Available', 'fill': 'lightblue'},
          'collection-complete': {'name': 'Data Available', 'fill': 'lightgreen'},
          'fully-complete': {'name': 'Data Available', 'fill': 'darkgreen'},
        }
      }),
      sm
    );
  }

  // bind hidden/reveal hooks
  document.querySelectorAll('[data-hidden]').forEach(e => e.style.display = "none");
  document.querySelectorAll('[data-reveal]').forEach(e => e.onclick = reveal);
});
