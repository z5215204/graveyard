import React, { useContext } from 'react'
import {Redirect, Route } from 'react-router-dom'
import AuthContext from '../AuthContext'

function ProtectedRoute(props) {
    const isSet = useContext(AuthContext);
    if(!isSet) {
        return <Redirect to="/login" />
    }
    return <Route {...props} />
}

export default ProtectedRoute