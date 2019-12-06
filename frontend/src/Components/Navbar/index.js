import React, { Component } from 'react'

import { Link } from '@reach/router'

const NavLink = props => (
  <Link
    {...props}
    getProps={({ isCurrent }) => {
      return {
        className: `navbar-item ${isCurrent && 'is-active'}`
      }
    }}
  />
)

export default class NavBar extends Component {
  constructor (props) {
    super(props)

    this.state = {
      isActive: false
    }

    this.handleToggleMenu = this.handleToggleMenu.bind(this)
  }

  handleToggleMenu (e) {
    e.preventDefault()
    this.setState({
      isActive: !this.state.isActive
    })
  }

  render () {
    const { isActive } = this.state
    return (
      <nav className='navbar is-dark' role='navigation' aria-label='main navigation'>
        <div className='navbar-brand'>
          <Link to='/' className='navbar-item'>
            <h1 className='is-size-4'>Caffeine</h1>
          </Link>
          <a
            role='button' onClick={this.handleToggleMenu} className={`navbar-burger burger ${isActive && 'is-active'}`} aria-label='menu' aria-expanded='false'
            data-target='navbar-menu'
          >
            <span aria-hidden='true' />
            <span aria-hidden='true' />
            <span aria-hidden='true' />
          </a>
        </div>

        <div id='navbar-menu' className={`navbar-menu ${isActive && 'is-active'}`}>
          <div className='navbar-start'>
            <NavLink to='/' className='navbar-item'>
                            Home
            </NavLink>

            <NavLink to='/login'>
                            Login
            </NavLink>
            <NavLink to='/not-found'>
                            Not Found
            </NavLink>

          </div>

        </div>
      </nav>
    )
  }
}
