import React, { Component } from 'react'
import Grapher from './grapher/Grapher'
import { Tabs, Tab } from 'react-bootstrap'

class App extends Component {
  render() {
    return (
      <div className="App">
      <Tabs defaultActiveKey={1} id="uncontrolled-tab-example">
        <Tab eventKey={1} title="Grapher">
          <Grapher />
          </Tab>
        </Tabs>
      </div>
    );
  }
}

export default App;
