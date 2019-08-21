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

  renderRow(p) {
    return (
      <tr key={p.id}>
        <td>{p.name}</td>
        <td>{applyTransforms(p.name, this.props.transforms)}</td>
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
            {this.props.precincts.map(this.renderRow)}
          </tbody>
        </table>
      </div>
    );
  }
}


class Merged extends React.Component {
  constructor(props) {
    super(props);
  }

  renderRow(m) {
    return (
      <tr key={m.sideA + m.sideB}>
        <td>{m.sideA}</td>
        <td>{m.sideB}</td>
        <td>{m.reason}</td>
      </tr>
    )
  }

  render() {
    return (
      <div>
        <h2 className="title is-3">Merged</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Side A</th>
              <th>Side B</th>
              <th>Merged Via</th>
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
      sideA: [
        {id: 1, name: "Goucho 1"},
        {id: 2, name: "Goucho 2"},
        {id: 3, name: "Goucho 3"},
        {id: 4, name: "Chal"},
        {id: 5, name: "Sochi"},
        {id: 6, name: "Zagin"},
      ],
      sideB: [
        {id: 1, name: "Goucho 01"},
        {id: 2, name: "Goucho 02"},
        {id: 3, name: "Goucho 03"},
        {id: 4, name: "C001"},
        {id: 5, name: "S001"},
        {id: 6, name: "Z001"},
      ],
      merged: [
        {"sideA": "Ableson", "sideB": "Ableson", "reason": "equal"},
        {"sideA": "Zoron", "sideB": "Zoron", "reason": "equal"},
      ],
      activeTransforms: [],
    };

    this.transformSelectRef = React.createRef();

    this.addTransform = this.addTransform.bind(this);
  }

  addTransform() {
    var transforms = [...this.state.activeTransforms];
    // TODO: enforce uniqueness
    transforms.push(this.transformSelectRef.current.value);
    this.setState({activeTransforms: transforms});
  }

  render() {
    return (
      <div>
        <div className="columns">
          <div className="column">
            <MergeTable title="Election Precincts" precincts={this.state.sideA} transforms={this.state.activeTransforms} />
          </div>
          <div className="column">
            <MergeTable title="Shapefile Precincts" precincts={this.state.sideB} transforms={this.state.activeTransforms} />
          </div>
        </div>

        <div>
          <select className="select" ref={this.transformSelectRef}>
            {Object.entries(TRANSFORMS).map(([k, v]) => (<option key={k} value={k}>{v.name}</option>))}
          </select>
          <button className="button" onClick={this.addTransform}>
            Add Transform
          </button>
          <ul>
            {this.state.activeTransforms.map((t) => <li key={t}>{t}</li>)}
          </ul>
        </div>
        <Merged matches={this.state.merged} />
      </div>
    );
  }
}
