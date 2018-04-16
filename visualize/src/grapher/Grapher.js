import React from 'react'
import Graph from 'react-graph-vis'
import taskData from '../data/tasks.json'
import './Grapher.css'

class Grapher extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            nodes: [],
            edges: [],
            events: []
        }
    }

    componentWillMount = () => {
        console.log(taskData)
        let tempEvents = []

        for(let key in taskData)
            if(taskData.hasOwnProperty(key))
                tempEvents = [...tempEvents, taskData[key]]

        this.setState({events: tempEvents})

        this.nodesFromEvents(tempEvents)
        this.edgesFromEvents(tempEvents)
    }

    edgesFromEvents = events => {
        let edges = []

        events.forEach(elem => {
            if(elem.previous.length > 0) {
                elem.previous.forEach(innerElem => {
                    let tempEdge = { from: innerElem, to: elem.taskID}

                    edges = [...edges, tempEdge]
                })
            }
        })

        this.setState({edges: edges})
    }

    nodesFromEvents = events => {
        let nodes = []
        let endingNode = {  //we need event which previous events are the events that wasn't previous of any
            id: "END",
            label: "End"
        }

        nodes = events.map(elem => {
            return {
                id: elem.taskID,
                label: "Task " + elem.taskID
            }
        }) 
        this.setState({nodes: nodes})
    }


    render() {
        let options = {
            layout: {
                hierarchical: {
                    enabled: true,
                    direction: "LR",
                    sortMethod: 'hubsize' //possibilites: hubsize, directed
                }
            }
            
        }

        let graph = {
            nodes: this.state.nodes,
            edges: this.state.edges
        }
        
        return(
            <div className="Graph">
                <Graph graph={graph} style={{ height: "100%" }} options={options}/>
            </div>
        )
    }

}

export default Grapher