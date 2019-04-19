import React from 'react'

const COLUMN_NAMES = {
  "stage": "Stage",
  "source_filename": "File Name",
  "created_at": "Date",
  "download_url": "Link"
}

export default class FileBrowser extends React.Component {

  constructor (props) {
    super(props);
    this.columns = ["stage", "source_filename", "created_at", "download_url"];
    this.renderRow = this.renderRow.bind(this);
  }

  renderRow(f) {
    var tds = [];
    var inner = "";
    for(var col of this.columns) {
      if(col === "download_url") {
        inner = (<a href={f.download_url}>download</a>);
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
    return (
      <tr>
        {this.columns.map(col => <td key={col}>{COLUMN_NAMES[col]}</td>)}
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
          { Object.values(this.props.files).map(this.renderRow) }
        </tbody>
      </table>
    );
  }
}
