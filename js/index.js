import React from 'react'
import ReactDOM from 'react-dom'

import StateMap from './state-map'

function reveal() {
  document.querySelector(`[data-hidden=${this.dataset.reveal}]`).style.display = "block";
  this.style.display = "none";
}


// TODO: get this data dynamically
window.addEventListener('load', () => {
  const sm = document.querySelector('[data-hook="state-map"]');
  if (sm) {
    ReactDOM.render(React.createElement(
      StateMap,
      {
        states: {
          'VA': 'available',
          'PA': 'available',
          'OH': 'available',
          'NJ': 'pending',
        },
        statuses: {
          'available': {'name': 'Data Available', 'fill': '#c7efcf'},
          'pending': {'name': 'In Progress', 'fill': 'beige'},
        }
      }),
      sm
    );
  }

  // bind hidden/reveal hooks
  document.querySelectorAll('[data-hidden]').forEach(e => e.style.display = "none");
  document.querySelectorAll('[data-reveal]').forEach(e => e.onclick = reveal);
});
