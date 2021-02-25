import React, {useState, useEffect} from 'react'
import io from "socket.io-client"
import Started from './GameComponents/Started'
import NotStarted from './GameComponents/NotStarted'
let socket
let ep = "localhost:5000/"

function Game(props) {
    const code = props.match.params.id
    const [name, setName] = useState(sessionStorage.getItem('name'))
    const [hand, setHand] = useState({'faceup': [], 'facedown': [], 'hand': []})
    const [joined, setJoined] = useState(false)
    const [started, setStarted] = useState(false)
    const [gameState, setGameState] = useState([])
    const [myTurn, setMyTurn] = useState(0)
    const [currTurn, setCurrTurn] = useState(0)
    const [joinMsg, setJoinMsg] = useState("")
    const [loading, setLoading] = useState(true)


    

    useEffect(() => {
        socket = io(ep)
        console.log('using effects heh')
        socket.emit('join', {'code': code, 'name': name})
        socket.on('setUser', (payload) => {
            sessionStorage.setItem('name', payload.name)
            setName(payload.name)
        })
        socket.on('isJoinSuccess', (payload) => {
            setGameState(payload.state)
            setJoinMsg(payload.msg)
            setJoined(payload.isJoined)
            setLoading(false)
        })
        socket.on('myTurn', (payload) => {
            setMyTurn(payload.myTurn)
        })
        socket.on('update', (payload) => {
            setCurrTurn(payload.turn)
            setGameState(payload.state)
            socket.emit('gethand', {'player': name, 'code': code})
        })
        socket.on('start', (payload) => {
            setCurrTurn(payload.turn)
            setStarted(payload.started)
            socket.emit('gethand', {'player': name, 'code': code})
        })
        socket.on('giveHand', (payload) => {
            setHand(payload.hand)
        })

        return () => {
            if (joined) {
                socket.emit('leave', {code: 'code'})
            }
        }
    }, [])

    if(loading) {
        return (
            <div>
                Loading...
            </div>
        )
    }

    if (!joined) {
        return (
            <div>
                {joinMsg}
            </div>
        )
    }

    if (!started) {
        return (
            <NotStarted code={code} socket={socket} />
        )
    }
    return (
        <Started code={code} socket={socket} />
    )

}

export default Game
export { socket }