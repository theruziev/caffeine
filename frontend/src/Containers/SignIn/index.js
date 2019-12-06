import React, { Component } from 'react'

import NavBar from '../../Components/Navbar'
import SignInForm from '../../Components/SignInForm'

export default class SignIn extends Component {
  render () {
    return (
      <div>
        <NavBar />

        <div className='container'>
          <div className='columns'>
            <div className='column is-4 is-offset-4'>
              <SignInForm />
            </div>
          </div>
        </div>
      </div>
    )
  }
}
