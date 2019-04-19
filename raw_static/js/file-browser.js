import React from 'react'

const COLUMN_NAMES = {
  "checkbox": "",
  "stage": "Stage",
  "source_filename": "File Name",
  "locality": "Locality",
  "cycle": "Cycle",
  "created_at": "Date",
  "download_url": "Link"
}

function sortBy(list, key, direction) {
  var newlist = [...list];
  newlist.sort(function(a, b) {
    if (a[key] < b[key]) { return -direction; }
    else if(a[key] > b[key]) { return direction;}
    else { return 0; }
  });
  return newlist;
}

export default class FileBrowser extends React.Component {

  constructor (props) {
    super(props);
    this.columns = ["checkbox", "stage", "locality", "cycle", "source_filename", "created_at", "download_url"];
    this.state = {
      columns: this.columns,
      sort: "locality",
      direction: 1,
    }
    this.renderRow = this.renderRow.bind(this);
    this.adjustSort = this.adjustSort.bind(this);
  }

  adjustSort(col) {
    if(this.state.sort === col) {
      this.setState({direction: -this.state.direction});
    } else {
      this.setState({sort: col, direction: 1})
    }
  }

  renderRow(f) {
    var tds = [];
    var inner = "";
    for(var col of this.state.columns) {
      if(col === "download_url") {
        inner = (<a href={f.download_url}>download</a>);
      } else if(col == "checkbox") {
        inner = (<input name="files" value={f.id} type="checkbox" />)
      } else {
        inner = f[col];
      }
      tds.push(<td key={col}>{inner}</td>);
    }
    return (
      <tr key={f.id}>{tds}</tr>
    );
  }

  renderHeader() {
    const sortArrow = this.state.direction === 1 ? (<i className="fas fa-arrow-down"></i>) : (<i className="fas fa-arrow-up"></i>);
    return (
      <tr>
        {this.columns.map(col => <td key={col} onClick={() => this.adjustSort(col)}>
        {COLUMN_NAMES[col]}
        &nbsp;{(this.state.sort === col ? sortArrow : "  ")}
        </td>)}
      </tr>
    );
  }

  render() {
    return (
      <table className="table">
        <thead>
          { this.renderHeader() }
        </thead>
        <tbody>
          { sortBy(this.props.files, this.state.sort, this.state.direction).map(this.renderRow) }
        </tbody>
      </table>
    );
  }
}
