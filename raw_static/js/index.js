import React from 'react'
import ReactDOM from 'react-dom'

import '../styles/main.scss'

import StateMap from './state-map'
import InteractiveMap from './interactive-map'
import StateMapInternal from './state-map-internal'

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
        },
        link_template: state => `/${state.toLowerCase()}`
      }),
      sm
    );
  }

  // bind hidden/reveal hooks
  document.querySelectorAll('[data-hidden]').forEach(e => e.style.display = "none");
  document.querySelectorAll('[data-reveal]').forEach(e => e.onclick = reveal);
});

window.addEventListener('load', () => {
  const im = document.querySelector('[data-hook="interactive-map"]');
  if (im) {
    const states = JSON.parse(document.getElementById('state-status').textContent);
    ReactDOM.render(React.createElement(
      InteractiveMap,
      {
        states: states,
        statuses: {
          'unknown': {'name': 'Unknown', 'fill': '#999'},
          // 'waiting': {'name': 'External Partner', 'fill': 'orange'},
          'collection': {'name': 'Collection In Progress', 'fill': 'lightblue'},
          'cleaning': {'name': 'Cleaning Data', 'fill': 'lightgreen'},
          'available': {'name': 'Data Available', 'fill': 'darkgreen'},
        },
        link_template: state => `/${state.toLowerCase()}`
      }),
      im
    );
  }

});

window.addEventListener('load', () => {
  const im = document.querySelector('[data-hook="state-map-internal"]');
  if (im) {
    const states = JSON.parse(document.getElementById('state-status').textContent);
    ReactDOM.render(React.createElement(
      StateMapInternal,
      {
        states: states,
        statuses: {
          'unknown': {'name': 'Unknown', 'fill': '#999'},
          // 'waiting': {'name': 'External Partner', 'fill': 'orange'},
          'collection': {'name': 'Collection In Progress', 'fill': 'lightblue'},
          'cleaning': {'name': 'Cleaning Data', 'fill': 'lightgreen'},
          'available': {'name': 'Data Available', 'fill': 'darkgreen'},
        },
        link_template: state => `/${state.toLowerCase()}`
      }),
      im
    );
  }

});

