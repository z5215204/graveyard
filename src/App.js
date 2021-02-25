import React, {useState} from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import logo from './logo.svg';
import './App.css';
import AuthContext from './AuthContext';
import ProtectedRoute from './Components/ProtectedRoute'
import Login from './Components/Login'
import Lobby from './Components/Lobby'
import Game from './Components/Game'


function App() {
  const [authDetails, setAuthDetails] = useState(sessionStorage.getItem("isSet"))

  function setAuth(isSet, name) {
    sessionStorage.setItem("isSet", isSet)
    sessionStorage.setItem("name", name)
    setAuthDetails(isSet)
  }

  return (
    <div className="App">
      <AuthContext.Provider value={authDetails}>
        <Router>
          <Switch>
            <Route exact path="/login" render={(props) => {
              return <Login {...props} setAuth={setAuth} />
            }} 
            />

            <ProtectedRoute exact path="/" render={(props) => {
              return <Lobby {...props} />
            }}
            />

            <ProtectedRoute exact path="/:id" render={(props) => {
              return <Game {...props} />
            }} 
            />            
          </Switch>
        </Router>

      </AuthContext.Provider>
    </div>
  );
}

export default App;
