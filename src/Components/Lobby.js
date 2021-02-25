import React, {useState} from 'react'
import {TextField, Box, Container, Button} from '@material-ui/core'
import axios from 'axios'

function Lobby(props) {
    const [join, setJoin] = useState(false)

    function handleSubmit(event) {
        event.preventDefault()
        const code = event.target[0].value
        console.log(code)
        if (!code) return
        props.history.push('/' + code)
    }

    function handleCreate(event) {
        axios.get('/api/create').then((response) =>{
            console.log(response)
            props.history.push('/' + response.data.game)
        })
        return
    }
    
    function handleJoin(event) {
        setJoin(!join)
    }

    if (!join) {
        return (
            <Container>
                <Box>
                    <Button onClick={handleCreate}>
                        Create Game
                    </Button>
                    <Button onClick={handleJoin}> 
                        Join Game
                    </Button>
                </Box>
            </Container>
        )
    }
    return (
        <Container>
            <Box>
                <p>Enter Code</p>
                <form onSubmit={handleSubmit}>
                    <TextField
                    required
                    autofocus
                    id='code'
                    label='Code'
                    variant='outlined'
                    inputProps={{maxLength: 4, minLength: 4}}
                    type='text'
                    />
                    <Button variant='contained' type='submit'>
                        Join
                    </Button>
                </form>
                <Button onClick={handleJoin}>
                        Back
                </Button>
            </Box>
        </Container>
    )

}

export default Lobby;