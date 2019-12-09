import React, { Component } from 'react'

import NavBar from '../../Components/Navbar'
import SignUpForm from '../../Components/SignUpForm'

export default class SignUp extends Component {
  render () {
    return (
      <div>
        <NavBar />

        <div className='container'>
          <div className='columns'>
            <div className='column is-4 is-offset-4'>
              <SignUpForm />
            </div>
          </div>
        </div>
      </div>
    )
  }
}
