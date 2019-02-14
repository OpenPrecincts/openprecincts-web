import React from 'react'
import ReactDOM from 'react-dom'

import StateMap from './state-map'

window.addEventListener('load', () => {
  const sm = document.querySelector('[data-hook="state-map"]');
  if (sm) {
    ReactDOM.render(React.createElement(
      StateMap,
      {
        states: {
          'VA': '#c7efcf',
          'PA': '#c7efcf',
          'OH': '#c7efcf',
          'NJ': '#cf0b67',
        },
      }),
      sm
    );
  }
});
