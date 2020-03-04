import React, { Component } from 'react'

import promiseFinally from "promise.prototype.finally";
import ReactDOM from 'react-dom'
import { Router } from '@reach/router'
import './index.scss'
import Home from './Containers/Home'
import NotFound from './Containers/NotFound'
import SignIn from './Containers/SignIn'
import SignUp from './Containers/SignUp'

import signInStore from './Store/SignInStore'
import userStore from './Store/UserStore'
import { Provider } from 'mobx-react'

const stores = {
  signInStore,
  userStore
}

// For easier debugging
window._____APP_STATE_____ = stores;

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


promiseFinally.shim();

ReactDOM.render(<Provider {...stores}>
  <App />
</Provider>, document.getElementById('root'))

// Hot Module Replacement
if (module.hot) {
  module.hot.accept()
}
