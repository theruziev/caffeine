import React, { Component } from 'react'

import NavBar from '../../Components/Navbar'
import SignInForm from '../../Components/SignInForm'
import { inject, observer } from 'mobx-react'

@inject('signInStore')
@observer
export default class SignIn extends Component {

  constructor (props, context) {
    super(props, context)
    this.handleSubmit = this.handleSubmit.bind(this)
  }

  handleSubmit (data) {
    this.props.signInStore.login(data)
  }

  render () {
    const isLoading = this.props.signInStore.isLoading
    const errors = this.props.signInStore.errors
    return (
      <div>
        <NavBar/>

        <div className='container'>
          <div className='columns'>
            <div className='column is-4 is-offset-4'>
              <SignInForm errors={errors} inputsDisabled={isLoading} submitDisabled={isLoading}
                          onSubmit={this.handleSubmit}/>
            </div>
          </div>
        </div>
      </div>
    )
  }
}
