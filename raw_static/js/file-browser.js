import React from 'react'

const COLUMN_NAMES = {
  "checkbox": "",
  "stage": "Stage",
  "source_filename": "File Name",
  "locality": "Locality",
  "cycle": "Cycle",
  "created_at": "Date",
  "download_url": "Link",
  "login_to_download": "",
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
    this.state = {
      columns: this.props.columns,
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
      switch(col) {
        case "download_url":
          inner = (<a href={f.download_url}>download</a>);
          break;
        case "checkbox":
          inner = (<input name="files" value={f.id} type="checkbox" />)
          break;
        case "login_to_download":
          inner = "login to download";
          break;
        default:
          inner = f[col];
          break;
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
        {this.state.columns.map(col => <td key={col} onClick={() => this.adjustSort(col)}>
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
