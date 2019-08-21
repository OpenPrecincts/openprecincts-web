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
  "normalize": {name: "Normalize Case", func: normalizeCase},
  "strip-zeroes": {name: "Strip Zeroes", func: stripZeroes},
}

function applyTransforms(s, transforms) {
  var result = s;
  for(var t of transforms) {
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
    if (e.matched === 1) {
      color = "lightgreen";
    } else if (e.matched > 1) {
      color = "red";
    }
    return (
      <tr key={k}>
        <td>{e.name}</td>
        <td style={{backgroundColor: color}}>{e.transformed}</td>
      </tr>
    )
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
          <tbody>
            {Object.entries(this.props.items).map(this.renderRow)}
          </tbody>
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
      <tr key={m.sideA.name + m.sideB.name}>
        <td>{m.sideA.name}</td>
        <td>{m.sideB.name}</td>
        <td>{m.reason.join(", ")}</td>
      </tr>
    )
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
          <tbody>
            {this.props.matches.map(this.renderRow)}
          </tbody>
        </table>
      </div>
    );
  }
}


export default class MergeTool extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      sideA: {
        101: {name: "Sloppy 1"},
        102: {name: "Sloppy 2"},
        103: {name: "Sloppy 3"},
        104: {name: "Cheeseboy"},
        105: {name: "Hurricane Puffy"},
        106: {name: "Zagnut"},
      },
      sideB: {
        201: {name: "SLOPPY 01"},
        202: {name: "SLOPPY 02"},
        203: {name: "SLOPPY 03"},
        204: {name: "C001"},
        205: {name: "S001"},
        206: {name: "Z001"},
      },
      matched: [],
      activeTransforms: [],
      proposedMatches: [],
    };

    this.transformSelectRef = React.createRef();

    this.addTransform = this.addTransform.bind(this);
    this.acceptProposed = this.acceptProposed.bind(this);
  }

  componentDidMount() {
    this.refreshTransforms([]);
  }

  checkMatches(sideA, sideB) {
    var proposedMatches = {}
    for(var [aId, a] of Object.entries(sideA)) {
      for(var [bId, b] of Object.entries(sideB)) {
        if (a.transformed === b.transformed) {
          proposedMatches[aId] = bId;
          a.matched += 1;
          b.matched += 1;
        }
      }
    }
    return proposedMatches;
  }

  addTransform() {
    var transforms = [...this.state.activeTransforms];
    if(!transforms.includes(this.transformSelectRef.current.value)) {
      transforms.push(this.transformSelectRef.current.value);
      this.refreshTransforms(transforms);
    }
  }

  acceptProposed() {
    var sideA = {...this.state.sideA};
    var sideB = {...this.state.sideB};
    var matched = [...this.state.matched];
    for(var [aId, bId] of Object.entries(this.state.proposedMatches)) {
      matched.push({
        sideA: sideA[aId],
        sideB: sideB[bId],
        reason: this.state.activeTransforms,
      });
      delete sideA[aId];
      delete sideB[bId];
    }
    this.setState({matched, sideA, sideB});
  }

  refreshTransforms(transforms) {
    var sideA = {...this.state.sideA};
    var sideB = {...this.state.sideB};

    for(var e of Object.values(sideA)) {
      e.transformed = applyTransforms(e.name, transforms);
      e.matched = 0;
    }
    for(var e of Object.values(sideB)) {
      e.transformed = applyTransforms(e.name, transforms);
      e.matched = 0;
    }
    const proposedMatches = this.checkMatches(sideA, sideB)

    this.setState({
      activeTransforms: transforms,
      sideA: sideA,
      sideB: sideB,
      proposedMatches: proposedMatches,
    });
  }

  render() {
    return (
      <div>
        <div className="columns">
          <div className="column">
            <MergeTable title="Election Precincts" items={this.state.sideA} transforms={this.state.activeTransforms} />
          </div>
          <div className="column">
            <MergeTable title="Shapefile Precincts" items={this.state.sideB} transforms={this.state.activeTransforms} />
          </div>
        </div>

        <div>
          <select className="select" ref={this.transformSelectRef}>
            {Object.entries(TRANSFORMS).map(([k, v]) => (
              this.state.activeTransforms.includes(k) ? "" : <option key={k} value={k}>{v.name}</option>)
            )}
          </select>
          <button className="button" onClick={this.addTransform}>
            Add Transform
          </button>
          <button className="button" onClick={() => this.refreshTransforms([])}>
            Reset Transforms
          </button>
          <ul>
            {this.state.activeTransforms.map((t) => <li key={t}>{t}</li>)}
          </ul>
        </div>

        <div>
          <h4 className="title is-4">Stats</h4>
          <dl>
            <dt>Side A Unmatched</dt>
            <dd>{Object.keys(this.state.sideA).length}</dd>
            <dt>Side B Unmatched</dt>
            <dd>{Object.keys(this.state.sideB).length}</dd>
            <dt>Proposed Matches</dt>
            <dd>{Object.keys(this.state.proposedMatches).length}</dd>
            <dt>Matched</dt>
            <dd>{this.state.matched.length}</dd>
          </dl>
          <button className="button" onClick={this.acceptProposed}>
            Accept Proposed Matches
          </button>
        </div>

        <Matched matches={this.state.matched} />
      </div>
    );
  }
}
