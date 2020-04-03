import React from "react";
import ReactMarkdown from 'react-markdown';

export default class ReadmeViewer extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
    };
  }



  componentDidMount() {
      Object.keys(this.props.readmes).map((id) => {
        fetch(`/files/download/${id}`)
        .then(res => res.text())
          .then((text) => {
              this.setState({
                  [id]: text
              })
          })
      })
  }

  render() {
    return (
        <div>
        <span className="is-size-4">File info:</span>
        {
            this.props.selectedReadmeId ?
            <ReactMarkdown
                source={this.state[this.props.selectedReadmeId]}
                className={"OP-Readme-Container box"}/>
            : <div className="is-size-5">
                Select a file on the left to view its info
            </div>
        }
        </div>
    );
  }
}
