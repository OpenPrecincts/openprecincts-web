import React from "react";

function normalizeCase(s) {
  return s.toLowerCase();
}

function stripZeroes(s) {
  const regex = /(\s)0+/gm;
  const subst = `$1`;
  return s.replace(regex, subst);
}

const TRANSFORMS = {
  normalize: { name: "Normalize Case", func: normalizeCase },
  "strip-zeroes": { name: "Strip Zeroes", func: stripZeroes },
};

function applyTransforms(s, transforms) {
  var result = s;
  for (var t of transforms) {
    var tfunc = TRANSFORMS[t].func;
    result = tfunc(result);
  }
  return result;
}

class MergeTable extends React.Component {
  constructor(props) {
    super(props);
    this.renderRow = this.renderRow.bind(this);
  }

  renderRow(item) {
    const [k, e] = item;
    var color = "white";
    if (e.clicked) {
      color = "lightgray";
    } else if (e.matched === 1) {
      color = "lightgreen";
    } else if (e.matched > 1) {
      color = "red";
    }
    return (
      <tr
        key={k}
        onClick={() => this.props.rowClick(k)}
        style={{ backgroundColor: color }}
      >
        <td>{e.name}</td>
        <td>{e.transformed}</td>
      </tr>
    );
  }

  render() {
    return (
      <div>
        <h2 className="title is-3">{this.props.title}</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Original</th>
              <th>Transformed</th>
            </tr>
          </thead>
          <tbody>{Object.entries(this.props.items).map(this.renderRow)}</tbody>
        </table>
      </div>
    );
  }
}

class Proposed extends React.Component {
  renderRow(m) {
    return (
      <tr key={`${m.sideA.id}+${m.sideB.id}`}>
        <td>{m.sideA.name}</td>
        <td>{m.sideB.name}</td>
      </tr>
    );
  }

  render() {
    return (
      <div>
        <h2 className="title is-3">Proposed</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Side A</th>
              <th>Side B</th>
            </tr>
          </thead>
          <tbody>{this.props.proposed.map(this.renderRow)}</tbody>
        </table>
      </div>
    );
  }
}

class Matched extends React.Component {
  constructor(props) {
    super(props);
  }

  renderRow(m) {
    return (
      <tr key={`${m.sideA.id}+${m.sideB.id}`}>
        <td>{m.sideA.name}</td>
        <td>{m.sideB.name}</td>
        <td>{m.reason.join(", ")}</td>
      </tr>
    );
  }

  render() {
    return (
      <div>
        <h2 className="title is-3">Matched</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Side A</th>
              <th>Side B</th>
              <th>Matched Via</th>
            </tr>
          </thead>
          <tbody>{this.props.matches.map(this.renderRow)}</tbody>
        </table>
      </div>
    );
  }
}

/* temporary random data functions */

const words = [
  "Sandy",
  "Bethel",
  "Tucker",
  "Capps",
  "Forrest",
  "Forset",
  "Aberdeen",
  "Thomas",
  "Armstrong",
  "Phenix",
  "Wythe",
  "Phoebus",
  "Smith",
  "McCoughtan",
  "Bryan",
  "Asbury",
  "Phillips",
  "Langley",
  "Booker",
  "Burbank",
  "Machen",
  "Mallory",
];

function choose(choices) {
  var index = Math.floor(Math.random() * choices.length);
  return choices[index];
}

function loadElectionPrecincts(n) {
  var sideA = {};
  var sideB = {};

  for (var i = 1; i < n; ++i) {
    var name = choose(words);
    var r = Math.random();

    if (r < 0.5) {
      name = name + " " + Math.floor(Math.random() * 20);
    } else {
      name = name + choose([" ", "-", "/", "--", "+"]) + choose(words);
    }

    sideA[i] = { id: i, name: name };

    if (Math.random() < 0.4) {
      name = name.toUpperCase();
    }
    if (Math.random() < 0.3) {
      // add a typo
      var pos = Math.floor(Math.random() * 6);
      name = name.slice(0, pos) + name.slice(pos + 1);
    }
    if (Math.random() < 0.3) {
      name = name.replace(" ", "      ");
    }
    if (Math.random() < 0.1) {
      name = name[0] + Math.floor(Math.random() * 100000);
    }
    sideB[200 + i] = { id: 200 + i, name: name };
  }

  return { sideA: sideA, sideB: sideB };
}

export default class MergeTool extends React.Component {
  constructor(props) {
    super(props);
    const d = loadElectionPrecincts(80);
    this.state = {
      sideA: d.sideA,
      sideB: d.sideB,
      matched: [],
      activeTransforms: [],
      proposedMatches: [],
    };

    this.transformSelectRef = React.createRef();

    this.addTransform = this.addTransform.bind(this);
    this.acceptProposed = this.acceptProposed.bind(this);
    this.mergeRowClick = this.mergeRowClick.bind(this);
    this.acceptManual = this.acceptManual.bind(this);
  }

  componentDidMount() {
    this.refreshTransforms([]);
  }

  checkMatches(sideA, sideB) {
    var proposedMatches = [];
    for (var [aId, a] of Object.entries(sideA)) {
      for (var [bId, b] of Object.entries(sideB)) {
        if (a.transformed === b.transformed) {
          proposedMatches.push({
            sideA: a,
            sideB: b,
            reason: this.state.activeTransforms,
          });
          a.matched += 1;
          b.matched += 1;
        }
      }
    }
    return proposedMatches;
  }

  addTransform() {
    var transforms = [...this.state.activeTransforms];
    if (!transforms.includes(this.transformSelectRef.current.value)) {
      transforms.push(this.transformSelectRef.current.value);
      this.refreshTransforms(transforms);
    }
  }

  acceptProposed() {
    var sideA = { ...this.state.sideA };
    var sideB = { ...this.state.sideB };
    var matched = [...this.state.matched];
    for (var match of this.state.proposedMatches) {
      matched.push(match);
      delete sideA[match.sideA.id];
      delete sideB[match.sideB.id];
    }
    this.setState({ matched, sideA, sideB, proposedMatches: [] });
  }

  mergeRowClick(clickedId) {
    var sideA = { ...this.state.sideA };
    var sideB = { ...this.state.sideB };
    var side;

    if (clickedId in sideA) {
      side = sideA;
      name = "sideA";
    } else if (clickedId in sideB) {
      side = sideB;
      name = "sideB";
    }

    for (var id in side) {
      if (id === clickedId) {
        side[id].clicked = !side[id].clicked;
      } else {
        side[id].clicked = false;
      }
    }
    this.setState({ name: side });
  }

  refreshTransforms(transforms) {
    var sideA = { ...this.state.sideA };
    var sideB = { ...this.state.sideB };

    for (var e of Object.values(sideA)) {
      e.transformed = applyTransforms(e.name, transforms);
      e.matched = 0;
    }
    for (var e of Object.values(sideB)) {
      e.transformed = applyTransforms(e.name, transforms);
      e.matched = 0;
    }
    const proposedMatches = this.checkMatches(sideA, sideB);

    this.setState({
      activeTransforms: transforms,
      sideA: sideA,
      sideB: sideB,
      proposedMatches: proposedMatches,
    });
  }

  acceptManual(e) {
    // if they hit enter, accept clicked
    if (e.keyCode === 13) {
      var aSelected, bSelected;
      for (var aId in this.state.sideA) {
        if (this.state.sideA[aId].clicked) {
          aSelected = aId;
          break;
        }
      }
      for (var bId in this.state.sideB) {
        if (this.state.sideB[bId].clicked) {
          bSelected = bId;
          break;
        }
      }

      // two are selected
      if (aSelected && bSelected) {
        var sideA = { ...this.state.sideA };
        var sideB = { ...this.state.sideB };
        var matched = [...this.state.matched];
        matched.push({
          sideA: sideA[aSelected],
          sideB: sideB[bSelected],
          reason: ["manual"],
        });
        delete sideA[aSelected];
        delete sideB[bSelected];
        this.setState({ matched, sideA, sideB });
      }
    }
  }

  render() {
    return (
      <div
        onKeyDown={this.acceptManual}
        tabIndex="0"
        style={{ outline: "none" }}
      >
        <div className="columns">
          <div className="column">
            <MergeTable
              title="Election Precincts"
              items={this.state.sideA}
              transforms={this.state.activeTransforms}
              rowClick={this.mergeRowClick}
            />
          </div>
          <div className="column">
            <MergeTable
              title="Shapefile Precincts"
              items={this.state.sideB}
              transforms={this.state.activeTransforms}
              rowClick={this.mergeRowClick}
            />
          </div>
        </div>

        <div>
          <select className="select" ref={this.transformSelectRef}>
            {Object.entries(TRANSFORMS).map(([k, v]) =>
              this.state.activeTransforms.includes(k) ? (
                ""
              ) : (
                <option key={k} value={k}>
                  {v.name}
                </option>
              )
            )}
          </select>
          <button className="button" onClick={this.addTransform}>
            Add Transform
          </button>
          <button className="button" onClick={() => this.refreshTransforms([])}>
            Reset Transforms
          </button>
          <ul>
            {this.state.activeTransforms.map(t => (
              <li key={t}>{t}</li>
            ))}
          </ul>
        </div>

        <div>
          <h4 className="title is-4">Stats</h4>
          <dl>
            <dt>Side A Unmatched</dt>
            <dd>{Object.keys(this.state.sideA).length}</dd>
            <dt>Side B Unmatched</dt>
            <dd>{Object.keys(this.state.sideB).length}</dd>
            <dt>Matched</dt>
            <dd>{this.state.matched.length}</dd>
          </dl>
        </div>

        <Proposed proposed={this.state.proposedMatches} />
        <button className="button is-primary" onClick={this.acceptProposed}>
          Accept Proposed Matches
        </button>
        <Matched matches={this.state.matched} />
      </div>
    );
  }
}
