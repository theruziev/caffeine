import React from 'react'
import NavBar from '../../Components/Navbar'
import styles from './index.scss'

export default class NotFound extends React.Component {
  render () {
    return (
      <div>
        <NavBar />
        <section className='hero'>
          <div className='hero-body'>
            <div className='container has-text-centered'>
              <p className={`title ${styles.bigStatusCode}`}>
                                404
              </p>
              <p className='subtitle'>
                                Not Found
              </p>
            </div>
          </div>
        </section>
      </div>
    )
  }
}
