import React, {useState, useEffect} from 'react'
import {TextField, Box, Container, Button} from '@material-ui/core'
import io from "socket.io-client"
import {socket} from '../Game'


function Started(props) {
    const name = sessionStorage.getItem('name')
    const [hand, setHand] = useState(props.myHand.map((card) => <li card />))
    const [lPlayed, setLPlayed] = useState(-1)
    const [nlPlayed, setNLPlayed] = useState(-1)
    const [nPlayers, setnPlayers] = useState(props.gamestate.length)
    const [updating, setUpdating] = useState(false)
    const [selectedCards, setSelectedCards] = useState([])

    useEffect(() => {
        socket.on('updating', (payload) => {
            setUpdating(payload.updating)
        })
    }, [])
    
    useEffect(() => {
        setHand((props.myHand).map((card) => <li card />))
    }, [props.hand])

    function handlePlay(event) {
        event.preventDefault()
        socket.emit('play', {'player': name, 'code': props.code, 'played': selectedCards})
    }

    function handleCardClick(card) {
        if (props.turn !== props.currTurn) return
        if (selectedCards.includes(card)) return
        
    }
   

    return (
        <div>
            Game has begun
        </div>
    )
}

export default Started