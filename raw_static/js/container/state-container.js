import React from "react";
import FileDownload from "../file-download";
import PrecinctMap from "../precinct-map";

export default class StateContainer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedElectionIndex: 0,
    };
    this.handleSelectElection = this.handleSelectElection.bind(this);
  }

  handleSelectElection(e) {
    this.setState({
      selectedElectionIndex: e.target.selectedIndex,
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

            <FileDownload
                filesByYear={this.props.filesByYear}
                selectedYear={selectedYear}
                elections={this.props.elections[selectedYear]} />
      </React.Fragment>
    );
  }
}
