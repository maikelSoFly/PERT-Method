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

        // for(let key in taskData)
        //     if(taskData.hasOwnProperty(key))
        //         tempEvents = [...tempEvents, taskData[key]]

        this.setState({events: taskData.taskData})
        let criticalPath = this.convertCriticalPath(taskData.criticalPath)
        this.nodesFromEvents(taskData.taskData, criticalPath)
        this.edgesFromEvents(taskData.taskData, criticalPath)
    }

    convertCriticalPath = criticalPath => {
        let criticalPathTmp = criticalPath.map(element => element.taskID)
        this.setState({criticalPath: criticalPathTmp})
        return criticalPathTmp
    }

    edgesFromEvents = (events, criticalPath) => {
        let edges = [],
            nodesOnEnds = []

        events.forEach(elem => {
            nodesOnEnds = [...nodesOnEnds, elem.taskID]
            if(elem.previous.length > 0) {
                elem.previous.forEach(innerElem => {
                    if(nodesOnEnds.indexOf(innerElem) >= 0) {
                        nodesOnEnds.splice(nodesOnEnds.indexOf(innerElem), 1)
                    }
                    let tempEdge = { from: innerElem, to: elem.taskID, color:{color: "#001dff"} }

                    let isInCritical = 0
                    criticalPath.forEach(element => {
                        if(element === tempEdge.from) isInCritical += 1
                        if(element === tempEdge.to) isInCritical += 1
                    })
                    if(isInCritical === 2) {
                        tempEdge.color.color = "#ff0000"
                        console.log("changing red")
                    }
                    

                    edges[edges.length] = tempEdge
                })
            }
        })

        console.log(edges)

        edges = [{from: "START", to: "A", color:{color: "#ff0000"}}, ...edges]

        nodesOnEnds.forEach(node => {
            let tempEdge = { from: node, to: "END", color:{color: undefined}}
           
            if(criticalPath.indexOf(node) !== -1) 
                tempEdge.color.color = "#ff0000"
            
                edges[edges.length] = tempEdge
        })

        this.setState({edges: edges})
    }

    nodesFromEvents = (events, criticalPath) => {
        let nodes = [],
            endingNode = {  //we need event which previous events are the events that wasn't previous of any
                id: "END",
                label: "End"
            },
            startingNode = {
                id: "START",
                label: "Start"
            }

        nodes = events.map(elem => {
            let tempNode = {
                id: elem.taskID,
                label: "| " + elem.times.minStart + " | " + elem.times.expected + " | " + elem.times.minEnd + " |\n" + "Task " + elem.taskID + "\n| " + elem.times.maxStart + " | " + elem.times.slack + " | " + elem.times.maxEnd + " |",
                // label: "Task " + elem.taskID + "\n|start|slack|end|\n|" + + "|" + elem.times.slack +"||" ,
                title: elem.text,
                color: {
                    border: "#001dff",
                    background: "#0090ff",
                }
            }

            if(criticalPath.indexOf(tempNode.id) !== -1) {
                tempNode.color.border = "#ff0000"
                tempNode.color.background = "#ff5959"
            }


            return tempNode
        }) 
        
        

        let legendNode =  {
            id: "legend",
            label: "| " + "min start" + " | " + "expected" + " | " + "min end" + " |\n\n" + "Task " + "id" + "\n\n| " + "max start" + " | " + "slack" + " | " + "max end" + " |",
            // title: elem.text,
            x: 20,
            y: 20,
            color: {
                border: "#000000",
                background: "#ffffff",
            }
        }

        nodes = [legendNode, startingNode, ...nodes, endingNode]

        this.setState({nodes: nodes})
    }


    render() {
        let options = {
            layout: {
                improvedLayout: false,
                hierarchical: {
                    treeSpacing: 200,
                    enabled: true,
                    direction: "LR",
                    sortMethod: 'directed' //possibilites: hubsize, directed
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