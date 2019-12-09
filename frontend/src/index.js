import React, { Component } from 'react'

import ReactDOM from 'react-dom'
import { Router } from '@reach/router'
import './index.scss'
import Home from './Containers/Home'
import NotFound from './Containers/NotFound'
import SignIn from './Containers/SignIn'
import SignUp from './Containers/SignUp'

export class App extends Component {
  render () {
    return (
      <Router>
        <Home path='/' />
        <SignIn path='/login' />
        <SignUp path='/signup' />
        <NotFound path='/not-found' default />
      </Router>)
  }
}

ReactDOM.render(<App />, document.getElementById('root'))

// Hot Module Replacement
if (module.hot) {
  module.hot.accept()
}
