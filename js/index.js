import React from 'react'
import ReactDOM from 'react-dom'

import StateMap from './state-map'

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
});
