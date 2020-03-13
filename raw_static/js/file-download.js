import React from "react";

export default class FileDownload extends React.Component {
  constructor(props) {
    super(props);
    this.renderFiletype = this.renderFiletype.bind(this);
  }

  renderFiletype(filetype) {
    switch(filetype) {
      case "zip":
        return "Shapefile";
      case "geojson":
        return "GeoJSON";
    }
  }

  render() {
    return (
      <div className="center">
        <span className="is-size-4">Downloads:</span>
        {
          Object.keys(this.props.filesByYear).map((year) => {
            return <div key={year} className={"FD-year-download box"}>
              <span className={"FD-year-title is-size-4"}>{year}</span>
              <div className={"FD-buttons"}>
              {
                Object.keys(this.props.filesByYear[year]).map((filetype) => {
                  return this.props.filesByYear[year][filetype].map((id) => {
                    return <a href={`/files/download/${id}`}
                              key={id}
                              className="button is-primary final-download">
                        <span className="file-icon">
                            <i className="fas fa-download"></i>
                        </span>
                        Download {this.renderFiletype(filetype)}
                    </a>
                  })
                })
              }
              </div>
            </div>
          })
        }
      </div>
    );
  }
}
