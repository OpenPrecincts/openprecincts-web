import React from 'react'
import ReactDOM from 'react-dom'

import '../styles/main.scss'

import StateMap from './state-map'
import FileBrowser from './file-browser'

function reveal() {
  document.querySelector(`[data-hidden=${this.dataset.reveal}]`).style.display = "block";
  this.style.display = "none";
}


function onFileChange() {
  if(this.files.length == 0) {
    document.querySelector(".file-name").innerHTML = "";
  } else if(this.files.length == 1) {
    document.querySelector(".file-name").innerHTML = this.files[0].name;
  } else {
    document.querySelector(".file-name").innerHTML = `${this.files.length} files`;
  }
};


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

  const fb = document.querySelector('[data-hook="file-browser"]');
  if (fb) {
    const files = JSON.parse(document.getElementById('files-data').textContent);
    ReactDOM.render(React.createElement(
      FileBrowser,
      {
        files: files,
        columns: files_columns,
      }),
      fb
    );
  }

  // bind hidden/reveal hooks
  document.querySelectorAll('[data-hidden]').forEach(e => e.style.display = "none");
  document.querySelectorAll('[data-reveal]').forEach(e => e.onclick = reveal);
  document.querySelectorAll('input[type=file]').forEach(e => e.onchange = onFileChange);
});
