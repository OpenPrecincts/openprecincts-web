import React from 'react'
import ReactDOM from 'react-dom'

import '../styles/main.scss'

import StateMap from './state-map'

function reveal() {
  document.querySelector(`[data-hidden=${this.dataset.reveal}]`).style.display = "block";
  this.style.display = "none";
}


window.addEventListener('load', () => {
  const sm = document.querySelector('[data-hook="state-map"]');
  if (sm) {
    const states = JSON.parse(document.getElementById('state-status').textContent);
    ReactDOM.render(React.createElement(
      StateMap,
      {
        states: states,
        statuses: {
          'unknown': {'name': 'Unknown', 'fill': '#999'},
          // 'waiting': {'name': 'External Partner', 'fill': 'orange'},
          'collection': {'name': 'Collection In Progress', 'fill': 'lightblue'},
          'cleaning': {'name': 'Cleaning Data', 'fill': 'lightgreen'},
          'available': {'name': 'Data Available', 'fill': 'darkgreen'},
        }
      }),
      sm
    );
  }

  // bind hidden/reveal hooks
  document.querySelectorAll('[data-hidden]').forEach(e => e.style.display = "none");
  document.querySelectorAll('[data-reveal]').forEach(e => e.onclick = reveal);
});
