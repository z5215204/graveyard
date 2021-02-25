import React from 'react';
import {TextField, Box, Container, Button} from '@material-ui/core'

function Login (props) {
    function handleSubmit(event) {
        event.preventDefault()
        const name = event.target[0].value
        console.log(name)
        if (!name) return
        props.setAuth(1,name)
        props.history.push('/')
    }

    return (
        <div>
        <Container>
            <p>Enter a Username</p>
            <Box>
                <form onSubmit={handleSubmit} >
                    <TextField
                    required
                    fullWidth
                    autofocus
                    id='name'
                    label='Username'
                    variant='outlined'
                    inputProps={{maxLength: 10}}
                    type='text'
                    />
                    <Button variant='contained' type='submit'>
                        Continue
                    </Button>
                </form>
            </Box>
        </Container>
        </div>
    )
}

export default Login