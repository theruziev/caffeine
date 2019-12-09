import React from 'react'

import useForm from 'react-hook-form'

export default function SignUpForm (props) {
  const { register, handleSubmit, errors, setError } = useForm()
  const onSubmit = data => {
    if (data.password !== data.repeat_password) {
      setError('repeat_password', 'notMatch', 'Password and repeat password is not match.')
    }
  }

  return (

    <form onSubmit={handleSubmit(onSubmit)}>

      <div className='field'>
        <label className='label'>Email</label>
        <div className='control'>
          <input ref={register({ required: true })} className={`input ${errors.username && 'is-danger'}`} name='username' type='text' placeholder='cafe@ephiopia.com' />
        </div>
        {errors.username && <p className='help is-danger'>Username or password is required</p>}
      </div>

      <div className='field'>
        <label className='label'>Password</label>
        <div className='control'>
          <input ref={register({ required: true })} className={`input ${errors.password && 'is-danger'}`} name='password' type='password' placeholder='You password' />
        </div>
        {errors.password && <p className='help is-danger'>The password is required</p>}

      </div>

      <div className='field'>
        <label className='label'>Repeat Password</label>
        <div className='control'>
          <input
            ref={register({ required: true })} className={`input ${errors.repeat_password && 'is-danger'}`}
            name='repeat_password' type='password' placeholder='Repeat you password'
          />
        </div>
        {errors.repeat_password && <p className='help is-danger'>{errors.repeat_password.message}</p>}

      </div>

      <div className='field  is-grouped is-grouped-right'>
        <div className='control'>
          <button className='button is-primary' type='submit'>Sign Up</button>
        </div>
      </div>
    </form>
  )
}
