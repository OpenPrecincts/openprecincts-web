import React from "react";

export default class FileDownload extends React.Component {
  constructor(props) {
    super(props);
    this.renderFiletype = this.renderFiletype.bind(this);
  }

  renderFiletype(mime_type) {
    switch(mime_type) {
      case "application/zip":
        return "Shapefile";
      case "application/vnd.geo+json":
        return "GeoJSON";
    }
  }

  formatBytes(bytes, decimals = 2) {
    // from https://stackoverflow.com/a/18650828 
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  render() {
    return (
      <div>
        <span className="is-size-4">Downloads:</span>
        <div className={"FD-files-grid"}>
        {
          Object.keys(this.props.files).map((id) => {
              return <div
                key={id}
                id={id}
                className={`FD-file box ${this.props.selectedFileId === id ? `FD-file-selected`: ``}`}>
                <div className={"FD-info"}>
                  <span>{this.props.files[id].filename}</span>
                  {
                    this.props.selectedFileId === id ? 
                    `Viewing file info`
                    : <a onClick={this.props.handleSelectReadme}>
                      View File Info
                    </a>
                  }
                </div>
                <a href={`/files/download/${id}`}
                          style={{ margin: 0 }}
                          key={id}
                          className="button is-primary final-download">
                    <span className="file-icon">
                        <i className="fas fa-download"></i>
                    </span>
                    Download {this.renderFiletype(this.props.files[id].mime_type)} ({this.formatBytes(this.props.files[id].size)})
                </a>
                {
                  this.props.files[id].elections.map((election) => {
                    return <span class={"tag"}>{election}</span>
                  })
                }
              </div>
          })
        }
        </div>
      </div>
    );
  }
}
