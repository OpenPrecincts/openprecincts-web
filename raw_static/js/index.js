import React from "react";
import ReactDOM from "react-dom";

import "../styles/main.scss";

import StateMap from "./state-map";
import FileBrowser from "./file-browser";
import MergeTool from "./mergetool";
import PrecinctMap from "./precinct-map";
import StateContainer from "./container/state-container";

function reveal() {
  document.querySelector(`[data-hidden=${this.dataset.reveal}]`).style.display =
    "block";
  this.style.display = "none";
}

function onFileChange() {
  if (this.files.length == 0) {
    document.querySelector(".file-name").innerHTML = "";
  } else if (this.files.length == 1) {
    document.querySelector(".file-name").innerHTML = this.files[0].name;
  } else {
    document.querySelector(
      ".file-name"
    ).innerHTML = `${this.files.length} files`;
  }
}

function initTabs() {
  function tabClick() {
    const clicked = this.dataset.tab;
    document.querySelectorAll("[data-tabbody]").forEach(function(t) {
      if (t.dataset.tabbody === clicked) {
        t.style.display = "block";
      } else {
        t.style.display = "none";
      }
    });
    document.querySelectorAll("[data-tab]").forEach(function(t) {
      if (t.dataset.tab === clicked) {
        t.parentNode.className = "is-active";
      } else {
        t.parentNode.className = "";
      }
    });
  }
  const tabs = document.querySelectorAll("[data-tab]");
  if (tabs.length) {
    tabs.forEach(t => (t.onclick = tabClick));
    tabs[0].click();
  }
}

window.addEventListener("load", () => {
  initTabs();

  const sm = document.querySelector('[data-hook="state-map"]');
  if (sm) {
    const states = JSON.parse(
      document.getElementById("state-status").textContent
    );
    ReactDOM.render(
      React.createElement(StateMap, {
        states: states,
        statuses: {
          "need-to-collect": { name: "Need to Collect", fill: "#999" },
          geography: { name: "Geography Collected", fill: "#6b94ae" },
          "election-data-linked": {
            name: "Election Data Linked",
            fill: "#87d67f",
          },
          "census-data-linked": { name: "Census Data Linked", fill: "#5cb253" },
          validated: { name: "Validated", fill: "#1c6414" },
        },
        link_template: state => `/${state.toLowerCase()}`,
      }),
      sm
    );
  }

  const fb = document.querySelector('[data-hook="file-browser"]');
  if (fb) {
    const files = JSON.parse(document.getElementById("files-data").textContent);
    ReactDOM.render(
      React.createElement(FileBrowser, {
        files: files,
        columns: files_columns,
      }),
      fb
    );
  }

  const mt = document.querySelector('[data-hook="mergetool"]');
  if (mt) {
    const featureProperties = JSON.parse(
      document.getElementById("feature_properties").textContent
    );
    ReactDOM.render(
      React.createElement(MergeTool, {
        state: mt.dataset.state,
        featureProperties: featureProperties,
      }),
      mt
    );
  }

  const readmes = JSON.parse(document.getElementById("readmes-data").textContent);
  const elections = JSON.parse(document.getElementById("elections-data").textContent);
  const files = JSON.parse(document.getElementById("files-data").textContent);
  const stateAbbrev = window.location.pathname.replace(/\//g, "");
  const sc = document.querySelector("[data-hook='state-container']");
  if (sc) {
    ReactDOM.render(
      React.createElement(StateContainer, {
        elections: elections,
        files: files,
        readmes: readmes,
        stateFromPath: stateAbbrev,
      }),
      sc
    );
  }

  // bind hidden/reveal hooks
  document
    .querySelectorAll("[data-hidden]")
    .forEach(e => (e.style.display = "none"));
  document.querySelectorAll("[data-reveal]").forEach(e => (e.onclick = reveal));
  document
    .querySelectorAll("input[type=file]")
    .forEach(e => (e.onchange = onFileChange));
});
