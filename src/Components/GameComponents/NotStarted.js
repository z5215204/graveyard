import React, {useState, useEffect} from 'react'
import {TextField, Box, Container, Button} from '@material-ui/core'
import io from "socket.io-client"
import { socket } from '../Game'

function NotStarted(props) {
    const [isDisabled, setIsDisabled] = useState(false)

    // useEffect(() => {
        
    // })

    function handleStart(event) {
        event.preventDefault()
        props.socket.emit('startGame', {'code': props.code})
        console.log("emitted")
    }

    return (
        <Container>
            <Box>
                <Button onClick={handleStart} disabled={isDisabled}>
                    Start Game
                </Button>
            </Box>
            <Box>
                
            </Box>
        </Container>
    )
}

export default NotStarted