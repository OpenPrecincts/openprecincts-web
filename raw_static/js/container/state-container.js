import React from "react";
import FileDownload from "../file-download";
import PrecinctMap from "../precinct-map";
import ReadmeViewer from "../readme-viewer";

export default class StateContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedElectionIndex: 0,
      selectedReadmeId: null,
    };
    this.handleSelectElection = this.handleSelectElection.bind(this);
    this.handleSelectReadme = this.handleSelectReadme.bind(this);
  }

  handleSelectElection(e) {
    this.setState({
      selectedElectionIndex: e.target.selectedIndex,
    })
  }

  handleSelectReadme(e) {
    const fileId = e.target.parentElement.parentElement.id;
    const fileElections = this.props.files[fileId].elections;
    Object.keys(this.props.readmes).filter((readmeId) => {
      const readmeElections = this.props.readmes[readmeId].elections;
      if (JSON.stringify(readmeElections) === JSON.stringify(fileElections)) {
        this.setState({
          selectedFileId: fileId,
          selectedReadmeId: readmeId
        })
      }
    })
  }

  render() {
    const selectedYear = this.props.elections[this.state.selectedElectionIndex].year || null;
    const selectedElectionType = this.props.elections[this.state.selectedElectionIndex].officeType || null;
    const selectedElection = this.props.elections.filter((election) => election.year === selectedYear && election.officeType === selectedElectionType) || null;

    return (
        <React.Fragment>
            <PrecinctMap
              stateFromPath={this.props.stateFromPath}
              selectedYear={selectedYear}
              handleSelectElection={this.handleSelectElection}
              elections={this.props.elections}
              {...selectedElection[0]} />
            <div className={"OP-State-Info-Container"}>
              <FileDownload
                selectedFileId={this.state.selectedFileId}
                handleSelectReadme={this.handleSelectReadme}
                files={this.props.files}
                selectedYear={selectedYear}
                elections={this.props.elections[selectedYear]} />
              <ReadmeViewer
                selectedReadmeId={this.state.selectedReadmeId}
                readmes={this.props.readmes}/>
            </div>
      </React.Fragment>
    );
  }
}
