import React from "react";
import FileDownload from "../file-download";
import PrecinctMap from "../precinct-map";

export default class StateContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedElectionIndex: 0,
      selectedYearIndex: 0,
    };
    this.handleSelectElection = this.handleSelectElection.bind(this);
    this.handleSelectYear = this.handleSelectYear.bind(this);
  }

  handleSelectYear(e) {
    this.setState({
      selectedYearIndex: e.target.selectedIndex,
    })
  }

  handleSelectElection(e) {
    this.setState({
      selectedElectionIndex: e.target.selectedIndex,
    })
  }

  render() {
    const selectedYear = Object.keys(this.props.electionsByYear)[this.state.selectedYearIndex];

    return (
        <React.Fragment>
            <PrecinctMap
                stateFromPath={this.props.stateFromPath}
                handleSelectYear={this.handleSelectYear}
                electionsByYear={this.props.electionsByYear}
                {...this.props.electionsByYear[selectedYear][this.state.selectedElectionIndex]} />

            <FileDownload
                filesByYear={this.props.filesByYear}
                selectedYear={selectedYear}
                selectedElectionIndex={this.state.selectedElectionIndex}
                elections={this.props.electionsByYear[selectedYear]} />
      </React.Fragment>
    );
  }
}
